/**
 * Authentication composable for Palabam
 * Handles authenticated users (parents, students, teachers) with magic link authentication
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
    if (!user.value) return null
    
    try {
      const { data, error } = await supabase
        .from('students')
        .select('id')
        .eq('user_id', user.value.id)
        .single()
      
      if (!error && data) {
        return data.id
      }
    } catch (err) {
      console.error('Error fetching student ID:', err)
    }
    
    return null
  }
  
  // Get teacher ID (from auth user -> teachers table)
  const getTeacherId = async (): Promise<string | null> => {
    if (!user.value) return null
    
    try {
      const { data, error } = await supabase
        .from('teachers')
        .select('id')
        .eq('user_id', user.value.id)
        .single()
      
      if (!error && data) {
        return data.id
      }
    } catch (err) {
      console.error('Error fetching teacher ID:', err)
    }
    
    return null
  }
  
  // Get parent ID (from auth user -> parents table)
  const getParentId = async (): Promise<string | null> => {
    if (!user.value) return null
    
    try {
      const { data, error } = await supabase
        .from('parents')
        .select('id')
        .eq('user_id', user.value.id)
        .single()
      
      if (!error && data) {
        return data.id
      }
    } catch (err) {
      console.error('Error fetching parent ID:', err)
    }
    
    return null
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
  
  // Sign up a new student (magic link)
  const signUpStudent = async (email: string, name: string) => {
    try {
      // Send magic link for signup
      const { data, error } = await supabase.auth.signInWithOtp({
        email,
        options: {
          data: {
            name,
            role: 'student'
          },
          emailRedirectTo: `${window.location.origin}/auth/callback`
        }
      })
      
      if (error) throw error
      
      // Note: User record and student record will be created after email verification
      // This happens in the auth callback handler
      return { success: true, message: 'Check your email for the magic link' }
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
  
  // Sign up a new teacher (magic link)
  const signUpTeacher = async (email: string, name: string) => {
    try {
      // Send magic link for signup
      const { data, error } = await supabase.auth.signInWithOtp({
        email,
        options: {
          data: {
            name,
            role: 'teacher'
          },
          emailRedirectTo: `${window.location.origin}/auth/callback`
        }
      })
      
      if (error) throw error
      
      return { success: true, message: 'Check your email for the magic link' }
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
  
  // Sign up a new parent (magic link)
  const signUpParent = async (email: string, name: string) => {
    try {
      // Send magic link for signup
      const { data, error } = await supabase.auth.signInWithOtp({
        email,
        options: {
          data: {
            name,
            role: 'parent'
          },
          emailRedirectTo: `${window.location.origin}/auth/callback`
        }
      })
      
      if (error) throw error
      
      return { success: true, message: 'Check your email for the magic link' }
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
  
  // Sign in with magic link (passwordless)
  const signInWithMagicLink = async (email: string) => {
    const { data, error } = await supabase.auth.signInWithOtp({
      email,
      options: {
        emailRedirectTo: `${window.location.origin}/auth/callback`
      }
    })
    
    if (error) throw error
    return { success: true, message: 'Check your email for the magic link' }
  }
  
  // Sign in with password (for demo accounts)
  const signInWithPassword = async (email: string, password: string) => {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password
    })
    
    if (error) throw error
    return { success: true, user: data.user }
  }
  
  // Legacy signIn function (now uses magic link)
  const signIn = async (email: string) => {
    return signInWithMagicLink(email)
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
    if (!user.value) return null
    
    try {
      const { data, error } = await supabase
        .from('users')
        .select('role')
        .eq('id', user.value.id)
        .single()
      
      if (error) return null
      return data?.role as 'student' | 'teacher' | 'admin' | 'parent' | null
    } catch (err) {
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
  
  // Sign up student via invite link
  const signUpStudentViaInvite = async (inviteCode: string, email: string, name: string) => {
    try {
      // First validate the invite code
      const inviteData = await validateInviteCode(inviteCode)
      if (!inviteData || !inviteData.valid) {
        throw new Error('Invalid invite code')
      }
      
      // Send magic link for signup with invite metadata
      const { data, error } = await supabase.auth.signInWithOtp({
        email,
        options: {
          data: {
            name,
            role: 'student',
            invite_code: inviteCode,
            class_id: inviteData.class_id
          },
          emailRedirectTo: `${window.location.origin}/auth/callback?invite=${inviteCode}`
        }
      })
      
      if (error) throw error
      
      return { success: true, message: 'Check your email for the magic link' }
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
    signInWithMagicLink,
    signInWithPassword,
    signOut,
    getUserRole,
    validateInviteCode,
    sendStudentInviteEmail,
    generateInviteLink
  }
}

