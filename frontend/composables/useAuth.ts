/**
 * Authentication composable for Palabam
 * Handles authenticated users (parents, students, teachers) with email/password authentication
 */
export const useAuth = () => {
  const supabase = useSupabaseClient()
  const user = useSupabaseUser()
  
  // Get current user ID
  const getUserId = (): string | null => {
    return user.value?.id || null
  }
  
  // Get student ID (from auth user -> students table)
  const getStudentId = async (): Promise<string | null> => {
    // Get user ID from reactive user or authenticated user
    let userId: string | null = null
    
    if (user.value?.id) {
      userId = user.value.id
    } else {
      // Fallback to authenticated user if reactive user is not ready
      const { data: userData } = await supabase.auth.getUser()
      userId = userData?.user?.id || null
    }
    
    if (!userId) {
      return null
    }
    
    try {
      const { data, error } = await supabase
        .from('students')
        .select('id')
        .eq('user_id', userId)
        .maybeSingle()
      
      if (error) {
        console.warn('Error fetching student ID:', error)
        return null
      }
      
      return data?.id || null
    } catch (err) {
      console.error('Exception fetching student ID:', err)
      return null
    }
  }
  
  // Get teacher ID (from auth user -> teachers table)
  const getTeacherId = async (): Promise<string | null> => {
    // Get user ID from reactive user or authenticated user
    let userId: string | null = null
    let userEmail: string | null = null
    let userName: string | null = null
    
    if (user.value?.id) {
      userId = user.value.id
      userEmail = user.value.email || null
      userName = user.value.user_metadata?.name || null
    } else {
      // Fallback to authenticated user if reactive user is not ready
      const { data: userData } = await supabase.auth.getUser()
      userId = userData?.user?.id || null
      userEmail = userData?.user?.email || null
      userName = userData?.user?.user_metadata?.name || null
    }
    
    if (!userId) {
      console.warn('getTeacherId: No user ID available')
      return null
    }
    
    console.log('getTeacherId: Checking for teacher record for user:', userId, 'email:', userEmail)
    
    try {
      // First check if teacher record exists
      const { data, error } = await supabase
        .from('teachers')
        .select('id')
        .eq('user_id', userId)
        .maybeSingle()
      
      console.log('getTeacherId: Teacher query result:', { data, error })
      
      if (error && error.code !== 'PGRST116') {
        console.warn('Error fetching teacher ID:', error)
        return null
      }
      
      // If teacher record exists, return it
      if (data?.id) {
        console.log('getTeacherId: Found existing teacher record:', data.id)
        return data.id
      }
      
      // Teacher record doesn't exist - check if user has teacher role
      const { data: userRecord, error: userError } = await supabase
        .from('users')
        .select('role, email')
        .eq('id', userId)
        .maybeSingle()
      
      console.log('getTeacherId: User record query result:', { userRecord, userError })
      
      // Ensure email and role are available in outer scope
      let email = userEmail || user.value?.email
      if (!email) {
        const { data: authUserData } = await supabase.auth.getUser()
        email = authUserData?.user?.email || null
      }
      
      let role = user.value?.user_metadata?.role
      if (!role) {
        const { data: authUserData } = await supabase.auth.getUser()
        role = authUserData?.user?.user_metadata?.role || null
      }
      
      // If user record doesn't exist (null) or there was an error, try to create it
      if (!userRecord || userError) {
        console.log('User record missing. Checking auth metadata to create user record...')
        
        // If we have a role, create the user record
        if (role) {
          console.log('Found role in metadata:', role, '- Creating user record...')
          if (email) {
            try {
              const { error: insertError } = await supabase.from('users').insert({
                id: userId,
                email: email,
                role: role
              })
              
              if (insertError) {
                // If it's a conflict (409), try using the backend API to fix data inconsistency
                if (insertError.code === '23505' || insertError.message?.includes('duplicate') || insertError.message?.includes('already exists') || insertError.code === '23503') {
                  console.log('User record conflict detected. Using backend API to ensure user record...')
                  try {
                    const config = useRuntimeConfig()
                    const apiUrl = config.public.apiUrl || 'http://localhost:8000'
                    const response = await $fetch(`${apiUrl}/api/users/ensure`, {
                      method: 'POST',
                      body: {
                        user_id: userId,
                        email: email,
                        role: role
                      }
                    })
                    console.log('User record ensured via API:', response)
                  } catch (apiError) {
                    console.error('Error ensuring user record via API:', apiError)
                    // Continue anyway - the record might exist
                  }
                } else {
                  console.error('Could not create user record:', insertError)
                }
              } else {
                console.log('User record created with role:', role)
              }
            } catch (e) {
              // Handle conflict errors gracefully
              if (e?.code === '23505' || e?.message?.includes('duplicate') || e?.message?.includes('already exists')) {
                console.log('User record already exists (conflict), trying API...')
                try {
                  const config = useRuntimeConfig()
                  const apiUrl = config.public.apiUrl || 'http://localhost:8000'
                  await $fetch(`${apiUrl}/api/users/ensure`, {
                    method: 'POST',
                    body: {
                      user_id: userId,
                      email: email,
                      role: role
                    }
                  })
                } catch (apiError) {
                  console.error('Error ensuring user record via API:', apiError)
                }
              } else {
                console.error('Could not create user record:', e)
              }
            }
          }
        } else if (email) {
          // Fallback: If no role in metadata, try to infer from email or check if teacher record exists
          // For demo accounts, check if email matches known teacher emails
          console.log('No role in metadata. Checking if this is a known teacher account...')
          const isKnownTeacher = email.includes('teacher@gauntlet.com') || email.includes('@gauntlet.com')
          
          if (isKnownTeacher) {
            // Check if there's already a teacher record (maybe created directly)
            const { data: existingTeacher } = await supabase
              .from('teachers')
              .select('id')
              .eq('user_id', userId)
              .maybeSingle()
            
            if (existingTeacher?.id) {
              console.log('Found existing teacher record, creating user record with teacher role')
              try {
                await supabase.from('users').insert({
                  id: userId,
                  email: email,
                  role: 'teacher'
                })
                console.log('User record created with inferred teacher role')
                role = 'teacher' // Set role for later use
              } catch (e) {
                console.error('Could not create user record:', e)
              }
            } else {
              // Assume teacher for demo accounts
              console.log('Assuming teacher role for demo account, creating user record...')
              try {
                const { error: insertError } = await supabase.from('users').insert({
                  id: userId,
                  email: email,
                  role: 'teacher'
                })
                
                if (insertError) {
                  // If it's a conflict (409), the record already exists - that's ok
                  if (insertError.code === '23505' || insertError.message?.includes('duplicate') || insertError.message?.includes('already exists')) {
                    console.log('User record already exists (conflict), that\'s ok')
                  } else {
                    console.error('Could not create user record:', insertError)
                  }
                } else {
                  console.log('User record created with assumed teacher role')
                }
                role = 'teacher' // Set role for later use
              } catch (e) {
                // Handle conflict errors gracefully
                if (e?.code === '23505' || e?.message?.includes('duplicate') || e?.message?.includes('already exists')) {
                  console.log('User record already exists (conflict), that\'s ok')
                  role = 'teacher' // Set role for later use
                } else {
                  console.error('Could not create user record:', e)
                }
              }
            }
          } else {
            console.warn('No role found in user metadata and cannot infer role. Cannot create user record.')
            return null
          }
        } else {
          console.warn('No role found in user metadata and no email available. Cannot create user record.')
          return null
        }
      }
      
      // Re-check user record after potential creation
      // Try multiple times in case of timing issues
      let finalUserRecord = null
      for (let attempt = 0; attempt < 3; attempt++) {
        const { data: userRecordAfter, error: userErrorAfter } = await supabase
          .from('users')
          .select('role, email')
          .eq('id', userId)
          .maybeSingle()
        
        console.log(`getTeacherId: User record after creation attempt ${attempt + 1}:`, { userRecordAfter, userErrorAfter })
        
        if (userRecordAfter) {
          finalUserRecord = userRecordAfter
          break
        }
        
        // Wait a bit before retrying
        if (attempt < 2) {
          await new Promise(resolve => setTimeout(resolve, 200))
        }
      }
      
      // If still no record, try querying by email as fallback
      if (!finalUserRecord && email) {
        console.log('Trying to find user record by email as fallback...')
        const { data: userByEmail } = await supabase
          .from('users')
          .select('role, email, id')
          .eq('email', email)
          .maybeSingle()
        
        console.log('User record found by email:', userByEmail)
        
        // If we found a record by email
        if (userByEmail) {
          if (userByEmail.id === userId) {
            // Perfect match - use it
            finalUserRecord = userByEmail
            console.log('Found user record by email with matching ID:', finalUserRecord)
          } else {
            // Data inconsistency: user record exists with different ID
            // This happens when there are multiple auth users with same email
            // We need to create a new user record with the correct ID
            // But email is unique, so we'll need to handle this differently
            console.warn(`User record exists with different ID (${userByEmail.id} vs ${userId}). This is a data inconsistency.`)
            console.log('Attempting to create user record with correct ID...')
            
            // Try to create user record - it will fail with 409, but we'll handle it
            // The role from the existing record can be used
            finalUserRecord = { role: userByEmail.role, email: userByEmail.email }
          }
        }
      }
      
      if (!finalUserRecord) {
        finalUserRecord = userRecord
      }
      
      // Determine user role from various sources
      const userRole = finalUserRecord?.role || role || (email?.includes('teacher@gauntlet.com') ? 'teacher' : null)
      
      console.log('Final determined role:', userRole, 'from finalUserRecord:', finalUserRecord, 'from metadata:', role)
      
      // If user has teacher role (or we can infer it), try to create teacher record
      if (userRole === 'teacher') {
        console.log('User has teacher role but no teacher record. Creating teacher record...')
        const name = userName || finalUserRecord?.email?.split('@')[0] || email?.split('@')[0] || 'Teacher'
        
        try {
          const { data: newTeacher, error: createError } = await supabase
            .from('teachers')
            .insert({
              user_id: userId,
              name
            })
            .select('id')
            .single()
          
          if (createError) {
            // If teacher record already exists, try to fetch it
            if (createError.code === '23505' || createError.message?.includes('duplicate') || createError.message?.includes('already exists')) {
              console.log('Teacher record may already exist, trying to fetch it...')
              const { data: existingTeacher } = await supabase
                .from('teachers')
                .select('id')
                .eq('user_id', userId)
                .maybeSingle()
              
              if (existingTeacher?.id) {
                console.log('Found existing teacher record:', existingTeacher.id)
                return existingTeacher.id
              }
            }
            console.error('Error creating teacher record:', createError)
            return null
          }
          
          console.log('Teacher record created successfully:', newTeacher.id)
          return newTeacher.id
        } catch (createErr) {
          console.error('Exception creating teacher record:', createErr)
          // Try to fetch existing record as fallback
          try {
            const { data: existingTeacher } = await supabase
              .from('teachers')
              .select('id')
              .eq('user_id', userId)
              .maybeSingle()
            
            if (existingTeacher?.id) {
              console.log('Found existing teacher record after error:', existingTeacher.id)
              return existingTeacher.id
            }
          } catch (fetchErr) {
            console.error('Error fetching existing teacher record:', fetchErr)
          }
          return null
        }
      } else {
        console.warn('User does not have teacher role. Role:', userRole, 'finalUserRecord:', finalUserRecord)
      }
      
      return null
    } catch (err) {
      console.error('Exception fetching teacher ID:', err)
      return null
    }
  }
  
  // Get parent ID (from auth user -> parents table)
  const getParentId = async (): Promise<string | null> => {
    // Get user ID from reactive user or authenticated user
    let userId: string | null = null
    
    if (user.value?.id) {
      userId = user.value.id
    } else {
      // Fallback to authenticated user if reactive user is not ready
      const { data: userData } = await supabase.auth.getUser()
      userId = userData?.user?.id || null
    }
    
    if (!userId) {
      return null
    }
    
    try {
      const { data, error } = await supabase
        .from('parents')
        .select('id')
        .eq('user_id', userId)
        .maybeSingle()
      
      if (error) {
        console.warn('Error fetching parent ID:', error)
        return null
      }
      
      return data?.id || null
    } catch (err) {
      console.error('Exception fetching parent ID:', err)
      return null
    }
  }
  
  // Get all children linked to current parent
  const getParentChildren = async (): Promise<Array<{ id: string; name: string; student_id: string }>> => {
    const parentId = await getParentId()
    if (!parentId) return []
    
    try {
      const { data, error } = await supabase
        .from('parent_students')
        .select(`
          student_id,
          students!inner (
            id,
            name
          )
        `)
        .eq('parent_id', parentId)
      
      if (error) throw error
      
      return (data || []).map((item: any) => ({
        id: item.students.id,
        name: item.students.name,
        student_id: item.student_id
      }))
    } catch (err) {
      console.error('Error fetching parent children:', err)
      return []
    }
  }
  
  // Link student to parent via student email
  const linkStudentToParent = async (studentEmail: string): Promise<boolean> => {
    const parentId = await getParentId()
    if (!parentId) {
      throw new Error('Parent not found')
    }
    
    try {
      // Find student by email
      const { data: userData, error: userError } = await supabase
        .from('users')
        .select('id, role')
        .eq('email', studentEmail)
        .eq('role', 'student')
        .single()
      
      if (userError || !userData) {
        throw new Error('Student not found with that email')
      }
      
      // Get student record
      const { data: studentData, error: studentError } = await supabase
        .from('students')
        .select('id')
        .eq('user_id', userData.id)
        .single()
      
      if (studentError || !studentData) {
        throw new Error('Student record not found')
      }
      
      // Create link (ignore if already exists)
      const { error: linkError } = await supabase
        .from('parent_students')
        .insert({
          parent_id: parentId,
          student_id: studentData.id
        })
      
      if (linkError) {
        // If already linked, that's fine
        if (linkError.code === '23505') { // Unique constraint violation
          return true
        }
        throw linkError
      }
      
      return true
    } catch (err: any) {
      console.error('Error linking student to parent:', err)
      throw err
    }
  }
  
  // Check if current user is a parent
  const isParent = async (): Promise<boolean> => {
    const role = await getUserRole()
    return role === 'parent'
  }
  
  // Sign up a new student (email/password)
  const signUpStudent = async (email: string, password: string, name: string) => {
    try {
      // Sign up with email and password
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: {
            name,
            role: 'student'
          }
        }
      })
      
      if (error) throw error
      
      if (!data.user) {
        throw new Error('Failed to create user account')
      }
      
      // Create user and student records immediately
      await createStudentRecord(data.user.id, email, name)
      
      return { success: true, user: data.user }
    } catch (error: any) {
      console.error('Sign up error:', error)
      throw error
    }
  }
  
  // Create student record after email verification
  const createStudentRecord = async (userId: string, email: string, name: string) => {
    try {
      // Create user record
      const { error: userError } = await supabase
        .from('users')
        .insert({
          id: userId,
          email,
          role: 'student'
        })
      
      if (userError) throw userError
      
      // Create student record
      const { data: studentData, error: studentError } = await supabase
        .from('students')
        .insert({
          user_id: userId,
          name
        })
        .select('id')
        .single()
      
      if (studentError) throw studentError
      
      return { studentId: studentData.id }
    } catch (error: any) {
      console.error('Error creating student record:', error)
      throw error
    }
  }
  
  // Sign up a new teacher (email/password)
  const signUpTeacher = async (email: string, password: string, name: string) => {
    try {
      // Sign up with email and password
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: {
            name,
            role: 'teacher'
          }
        }
      })
      
      if (error) throw error
      
      if (!data.user) {
        throw new Error('Failed to create user account')
      }
      
      // Create user and teacher records immediately
      await createTeacherRecord(data.user.id, email, name)
      
      return { success: true, user: data.user }
    } catch (error: any) {
      console.error('Sign up error:', error)
      throw error
    }
  }
  
  // Create teacher record after email verification
  const createTeacherRecord = async (userId: string, email: string, name: string) => {
    try {
      // Create user record
      const { error: userError } = await supabase
        .from('users')
        .insert({
          id: userId,
          email,
          role: 'teacher'
        })
      
      if (userError) throw userError
      
      // Create teacher record
      const { data: teacherData, error: teacherError } = await supabase
        .from('teachers')
        .insert({
          user_id: userId,
          name
        })
        .select('id')
        .single()
      
      if (teacherError) throw teacherError
      
      return { teacherId: teacherData.id }
    } catch (error: any) {
      console.error('Error creating teacher record:', error)
      throw error
    }
  }
  
  // Sign up a new parent (email/password)
  const signUpParent = async (email: string, password: string, name: string) => {
    try {
      // Sign up with email and password
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: {
            name,
            role: 'parent'
          }
        }
      })
      
      if (error) throw error
      
      if (!data.user) {
        throw new Error('Failed to create user account')
      }
      
      // Create user and parent records immediately
      await createParentRecord(data.user.id, email, name)
      
      // Link to children if provided
      const signupDataStr = sessionStorage.getItem('signup_data')
      if (signupDataStr) {
        try {
          const signupData = JSON.parse(signupDataStr)
          if (signupData.children && Array.isArray(signupData.children)) {
            for (const child of signupData.children) {
              if (child.email) {
                try {
                  await linkStudentToParent(child.email)
                } catch (err) {
                  console.warn('Could not link to student:', err)
                }
              }
            }
          }
          sessionStorage.removeItem('signup_data')
        } catch (err) {
          console.warn('Error processing signup data:', err)
        }
      }
      
      return { success: true, user: data.user }
    } catch (error: any) {
      console.error('Sign up error:', error)
      throw error
    }
  }
  
  // Create parent record after email verification
  const createParentRecord = async (userId: string, email: string, name: string) => {
    try {
      // Create user record
      const { error: userError } = await supabase
        .from('users')
        .insert({
          id: userId,
          email,
          role: 'parent'
        })
      
      if (userError) throw userError
      
      // Create parent record
      const { data: parentData, error: parentError } = await supabase
        .from('parents')
        .insert({
          user_id: userId,
          name
        })
        .select('id')
        .single()
      
      if (parentError) throw parentError
      
      return { parentId: parentData.id }
    } catch (error: any) {
      console.error('Error creating parent record:', error)
      throw error
    }
  }
  
  // Sign in with password
  const signInWithPassword = async (email: string, password: string) => {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password
    })
    
    if (error) throw error
    return { success: true, user: data.user }
  }
  
  // Legacy signIn function (now uses password)
  const signIn = async (email: string, password: string) => {
    return signInWithPassword(email, password)
  }
  
  // Sign out
  const signOut = async () => {
    const { error } = await supabase.auth.signOut()
    if (error) throw error
    
    // Clear cookies
    useCookie('student_id').value = null
    useCookie('teacher_id').value = null
    useCookie('student_name').value = null
  }
  
  // Get user role
  const getUserRole = async (): Promise<'student' | 'teacher' | 'admin' | 'parent' | null> => {
    // Get user ID from reactive user or authenticated user
    let userId: string | null = null
    let userMetadata: any = null
    let userEmail: string | null = null
    
    if (user.value?.id) {
      userId = user.value.id
      userMetadata = user.value.user_metadata
      userEmail = user.value.email || null
    } else {
      // Fallback to authenticated user if reactive user is not ready
      // Use getUser() instead of getSession() for security
      const { data: userData } = await supabase.auth.getUser()
      userId = userData?.user?.id || null
      userMetadata = userData?.user?.user_metadata || null
      userEmail = userData?.user?.email || null
    }
    
    if (!userId) {
      return null
    }
    
    try {
      // Use maybeSingle() instead of single() to handle case where user doesn't exist in public.users
      const { data, error } = await supabase
        .from('users')
        .select('role')
        .eq('id', userId)
        .maybeSingle()
      
      if (error) {
        // If user doesn't exist in public.users, try to create it from metadata
        if (error.code === 'PGRST116' || error.message?.includes('0 rows')) {
          const role = userMetadata?.role || null
          if (role && ['student', 'teacher', 'parent', 'admin'].includes(role) && userEmail) {
            // Try to create the user record
            try {
              await supabase
                .from('users')
                .insert({
                  id: userId,
                  email: userEmail,
                  role
                })
              // Return the role we just created
              return role as 'student' | 'teacher' | 'admin' | 'parent'
            } catch (createError) {
              console.warn('Failed to create user record:', createError)
            }
          }
        }
        console.warn('Error fetching user role:', error)
        return null
      }
      
      // If no data but no error, user doesn't exist - try metadata fallback
      if (!data && userMetadata?.role) {
        return userMetadata.role as 'student' | 'teacher' | 'admin' | 'parent' | null
      }
      
      return data?.role as 'student' | 'teacher' | 'admin' | 'parent' | null
    } catch (err) {
      console.warn('Exception fetching user role:', err)
      // Fallback to metadata if available
      if (userMetadata?.role) {
        return userMetadata.role as 'student' | 'teacher' | 'admin' | 'parent' | null
      }
      return null
    }
  }
  
  // Validate invite code and get class info
  const validateInviteCode = async (code: string) => {
    const config = useRuntimeConfig()
    const apiUrl = config.public.apiUrl || 'http://localhost:8000'
    
    try {
      const response = await $fetch(`${apiUrl}/api/invites/${code}`)
      return response
    } catch (error: any) {
      console.error('Error validating invite code:', error)
      throw error
    }
  }
  
  // Sign up student via invite link (email/password)
  const signUpStudentViaInvite = async (inviteCode: string, email: string, password: string, name: string) => {
    try {
      // First validate the invite code
      const inviteData = await validateInviteCode(inviteCode)
      if (!inviteData || !inviteData.valid) {
        throw new Error('Invalid invite code')
      }
      
      // Sign up with email and password
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: {
            name,
            role: 'student',
            invite_code: inviteCode,
            class_id: inviteData.class_id
          }
        }
      })
      
      if (error) throw error
      
      if (!data.user) {
        throw new Error('Failed to create user account')
      }
      
      // Create student record and accept invite immediately
      await createStudentRecordWithInvite(data.user.id, email, name, inviteCode)
      
      return { success: true, user: data.user }
    } catch (error: any) {
      console.error('Sign up error:', error)
      throw error
    }
  }
  
  // Create student record after email verification (with invite acceptance)
  const createStudentRecordWithInvite = async (userId: string, email: string, name: string, inviteCode: string) => {
    const config = useRuntimeConfig()
    const apiUrl = config.public.apiUrl || 'http://localhost:8000'
    
    try {
      // Create user record
      const { error: userError } = await supabase
        .from('users')
        .insert({
          id: userId,
          email,
          role: 'student'
        })
      
      if (userError) throw userError
      
      // Create student record
      const { data: studentData, error: studentError } = await supabase
        .from('students')
        .insert({
          user_id: userId,
          name
        })
        .select('id')
        .single()
      
      if (studentError) throw studentError
      
      // Accept invite via API (this will join the class)
      await $fetch(`${apiUrl}/api/invites/${inviteCode}/accept`, {
        method: 'POST',
        body: {
          email,
          name
        }
      })
      
      return { studentId: studentData.id }
    } catch (error: any) {
      console.error('Error creating student record with invite:', error)
      throw error
    }
  }
  
  // Accept invite for existing logged-in student
  const acceptInviteForExistingStudent = async (inviteCode: string, email: string) => {
    const config = useRuntimeConfig()
    const apiUrl = config.public.apiUrl || 'http://localhost:8000'
    
    try {
      // Get student name from user metadata or student record
      let name = user.value?.user_metadata?.name || ''
      
      if (!name) {
        // Try to get name from student record
        const { data: studentData } = await supabase
          .from('students')
          .select('name')
          .eq('user_id', user.value?.id)
          .single()
        
        if (studentData) {
          name = studentData.name
        }
      }
      
      if (!name) {
        // Fallback to email username
        name = email.split('@')[0]
      }
      
      // Accept invite via API
      const response = await $fetch(`${apiUrl}/api/invites/${inviteCode}/accept`, {
        method: 'POST',
        body: {
          email,
          name
        }
      })
      
      return response
    } catch (error: any) {
      console.error('Error accepting invite for existing student:', error)
      throw error
    }
  }
  
  // Send student invite via email (deprecated - use direct API call with teacher_id)
  const sendStudentInviteEmail = async (classId: string, email: string) => {
    const config = useRuntimeConfig()
    const apiUrl = config.public.apiUrl || 'http://localhost:8000'
    const teacherId = await getTeacherId()
    if (!teacherId) {
      throw new Error('Teacher not found')
    }
    
    try {
      const response = await $fetch(`${apiUrl}/api/invites/email`, {
        method: 'POST',
        body: {
          class_id: classId,
          email,
          teacher_id: teacherId
        }
      })
      return response
    } catch (error: any) {
      console.error('Error sending invite email:', error)
      throw error
    }
  }
  
  // Generate shareable invite link (deprecated - use direct API call with teacher_id)
  const generateInviteLink = async (classId: string) => {
    const config = useRuntimeConfig()
    const apiUrl = config.public.apiUrl || 'http://localhost:8000'
    const teacherId = await getTeacherId()
    if (!teacherId) {
      throw new Error('Teacher not found')
    }
    
    try {
      const response = await $fetch(`${apiUrl}/api/invites/generate`, {
        method: 'POST',
        body: {
          class_id: classId,
          teacher_id: teacherId
        }
      })
      return response
    } catch (error: any) {
      console.error('Error generating invite link:', error)
      throw error
    }
  }
  
  return {
    user: readonly(user),
    getUserId,
    getStudentId,
    getTeacherId,
    getParentId,
    getParentChildren,
    linkStudentToParent,
    isParent,
    signUpStudent,
    signUpTeacher,
    signUpParent,
    signUpStudentViaInvite,
    createStudentRecord,
    createStudentRecordWithInvite,
    createTeacherRecord,
    createParentRecord,
    signIn,
    signInWithPassword,
    signOut,
    getUserRole,
    validateInviteCode,
    acceptInviteForExistingStudent,
    sendStudentInviteEmail,
    generateInviteLink
  }
}

