<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <!-- Navigation Header -->
    <header class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 sticky top-0 z-50">
      <UContainer>
        <div class="flex items-center justify-between h-16">
          <!-- Logo and Brand -->
          <NuxtLink to="/" class="flex items-center gap-2">
            <div class="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
              <UIcon name="i-heroicons-academic-cap" class="text-white text-lg" />
            </div>
            <span class="text-xl font-bold text-gray-900 dark:text-white">Palabam</span>
          </NuxtLink>

          <!-- Navigation Links -->
          <nav class="hidden md:flex items-center gap-1">
            <template v-if="user">
              <!-- Parent Navigation -->
              <template v-if="userRole === 'parent'">
                <UButton
                  to="/parent/dashboard"
                  variant="ghost"
                  :class="{ 'bg-primary/10 text-primary': $route.path.startsWith('/parent') }"
                >
                  Dashboard
                </UButton>
              </template>
              <!-- Student Navigation -->
              <template v-else-if="userRole === 'student'">
                <UButton
                  to="/student/dashboard"
                  variant="ghost"
                  :class="{ 'bg-primary/10 text-primary': $route.path.startsWith('/student') }"
                >
                  My Progress
                </UButton>
                <UButton
                  to="/story-spark"
                  variant="ghost"
                  :class="{ 'bg-primary/10 text-primary': $route.path === '/story-spark' }"
                >
                  Story Spark
                </UButton>
              </template>
              <!-- Teacher Navigation -->
              <template v-else-if="userRole === 'teacher'">
                <UButton
                  to="/dashboard"
                  variant="ghost"
                  :class="{ 'bg-primary/10 text-primary': $route.path === '/dashboard' }"
                >
                  Dashboard
                </UButton>
                <UButton
                  to="/upload"
                  variant="ghost"
                  :class="{ 'bg-primary/10 text-primary': $route.path === '/upload' }"
                >
                  Upload
                </UButton>
                <UButton
                  to="/spark"
                  variant="ghost"
                  :class="{ 'bg-primary/10 text-primary': $route.path === '/spark' || $route.path === '/story-spark' }"
                >
                  Story Spark
                </UButton>
              </template>
            </template>
            <!-- Public Navigation -->
            <template v-else>
              <UButton
                to="/login"
                variant="ghost"
                :class="{ 'bg-primary/10 text-primary': $route.path === '/login' }"
              >
                Login
              </UButton>
              <UButton
                to="/signup"
                variant="ghost"
                :class="{ 'bg-primary/10 text-primary': $route.path === '/signup' }"
              >
                Sign Up
              </UButton>
            </template>
          </nav>

          <!-- Right side: User menu, Dark mode toggle and mobile menu -->
          <div class="flex items-center gap-2">
            <!-- User Menu (if authenticated) -->
            <template v-if="user">
              <UDropdownMenu :items="userMenuItems">
                <UButton
                  variant="ghost"
                  :icon="userRole === 'parent' ? 'i-heroicons-user-group' : userRole === 'student' ? 'i-heroicons-user' : 'i-heroicons-academic-cap'"
                  class="flex items-center gap-2"
                >
                  <span class="hidden sm:inline">{{ userRole || 'User' }}</span>
                  <UIcon name="i-heroicons-chevron-down" class="w-4 h-4" />
                </UButton>
              </UDropdownMenu>
            </template>
            
            <!-- Dark Mode Toggle - Always visible -->
            <UButton
              @click="toggleColorMode"
              variant="ghost"
              :icon="colorMode.value === 'dark' ? 'i-heroicons-sun' : 'i-heroicons-moon'"
              :aria-label="colorMode.value === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'"
              class="flex-shrink-0"
            />
            
            <!-- Mobile Menu Button -->
            <UButton
              @click="mobileMenuOpen = !mobileMenuOpen"
              variant="ghost"
              icon="i-heroicons-bars-3"
              class="md:hidden"
            />
          </div>
        </div>

        <!-- Mobile Menu -->
        <div v-if="mobileMenuOpen" class="md:hidden border-t border-gray-200 dark:border-gray-700 py-4">
          <div class="flex flex-col gap-2">
            <template v-if="user">
              <!-- Parent Mobile Menu -->
              <template v-if="userRole === 'parent'">
                <UButton
                  to="/parent/dashboard"
                  variant="ghost"
                  block
                  :class="{ 'bg-primary/10 text-primary': $route.path.startsWith('/parent') }"
                  @click="mobileMenuOpen = false"
                >
                  Dashboard
                </UButton>
              </template>
              <!-- Student Mobile Menu -->
              <template v-else-if="userRole === 'student'">
                <UButton
                  to="/student/dashboard"
                  variant="ghost"
                  block
                  :class="{ 'bg-primary/10 text-primary': $route.path.startsWith('/student') }"
                  @click="mobileMenuOpen = false"
                >
                  My Progress
                </UButton>
                <UButton
                  to="/story-spark"
                  variant="ghost"
                  block
                  :class="{ 'bg-primary/10 text-primary': $route.path === '/story-spark' }"
                  @click="mobileMenuOpen = false"
                >
                  Story Spark
                </UButton>
              </template>
              <!-- Teacher Mobile Menu -->
              <template v-else-if="userRole === 'teacher'">
                <UButton
                  to="/dashboard"
                  variant="ghost"
                  block
                  :class="{ 'bg-primary/10 text-primary': $route.path === '/dashboard' }"
                  @click="mobileMenuOpen = false"
                >
                  Dashboard
                </UButton>
                <UButton
                  to="/upload"
                  variant="ghost"
                  block
                  :class="{ 'bg-primary/10 text-primary': $route.path === '/upload' }"
                  @click="mobileMenuOpen = false"
                >
                  Upload
                </UButton>
                <UButton
                  to="/spark"
                  variant="ghost"
                  block
                  :class="{ 'bg-primary/10 text-primary': $route.path === '/spark' || $route.path === '/story-spark' }"
                  @click="mobileMenuOpen = false"
                >
                  Story Spark
                </UButton>
              </template>
              <div class="border-t border-gray-200 dark:border-gray-700 my-2"></div>
              <UButton
                variant="ghost"
                block
                color="error"
                icon="i-heroicons-arrow-right-on-rectangle"
                @click="handleLogout"
              >
                Logout
              </UButton>
            </template>
            <!-- Public Mobile Menu -->
            <template v-else>
              <UButton
                to="/login"
                variant="ghost"
                block
                :class="{ 'bg-primary/10 text-primary': $route.path === '/login' }"
                @click="mobileMenuOpen = false"
              >
                Login
              </UButton>
              <UButton
                to="/signup"
                variant="ghost"
                block
                :class="{ 'bg-primary/10 text-primary': $route.path === '/signup' }"
                @click="mobileMenuOpen = false"
              >
                Sign Up
              </UButton>
            </template>
          </div>
        </div>
      </UContainer>
    </header>

    <!-- Main Content -->
    <main>
      <slot />
    </main>

    <!-- Footer -->
    <footer class="text-white mt-16" style="background-color: #04232e;">
      <UContainer class="py-8">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <div class="flex items-center gap-2 mb-4">
              <div class="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                <UIcon name="i-heroicons-academic-cap" class="text-white text-lg" />
              </div>
              <span class="text-xl font-bold text-white" style="color: #ffffff;">Palabam</span>
            </div>
            <p class="text-white text-sm leading-relaxed" style="color: #ffffff;">
              Personalized vocabulary recommendations for educators
            </p>
          </div>
          <div>
            <h3 class="font-semibold mb-4 text-white" style="color: #ffffff;">Quick Links</h3>
            <ul class="space-y-2.5 text-sm" style="color: #ffffff;">
              <li>
                <NuxtLink to="/dashboard" class="hover:text-white transition-colors" style="color: #ffffff;">
                  Dashboard
                </NuxtLink>
              </li>
              <li>
                <NuxtLink to="/upload" class="hover:text-white transition-colors" style="color: #ffffff;">
                  Upload Student Work
                </NuxtLink>
              </li>
              <li>
                <NuxtLink to="/story-spark" class="hover:text-white transition-colors" style="color: #ffffff;">
                  Story Spark
                </NuxtLink>
              </li>
            </ul>
          </div>
          <div>
            <h3 class="font-semibold mb-4 text-white" style="color: #ffffff;">About</h3>
            <p class="text-sm leading-relaxed" style="color: #ffffff;">
              Palabam helps educators identify vocabulary gaps and provide personalized word recommendations for their students.
            </p>
          </div>
        </div>
        <div class="border-t mt-8 pt-8 text-center text-sm" style="border-color: rgba(255, 255, 255, 0.3); color: #ffffff;">
          <p>&copy; {{ new Date().getFullYear() }} Palabam. All rights reserved.</p>
        </div>
      </UContainer>
    </footer>
  </div>
</template>

<script setup lang="ts">
const { user, getUserRole, signOut } = useAuth()
const router = useRouter()
const colorMode = useColorMode()

const mobileMenuOpen = ref(false)
const userRole = ref<'parent' | 'student' | 'teacher' | 'admin' | null>(null)

// Fetch user role
onMounted(async () => {
  if (user.value) {
    userRole.value = await getUserRole()
  }
})

// Watch for auth changes
watch(user, async (newUser) => {
  if (newUser) {
    userRole.value = await getUserRole()
  } else {
    userRole.value = null
  }
})

const toggleColorMode = () => {
  colorMode.preference = colorMode.value === 'dark' ? 'light' : 'dark'
}

const handleLogout = async () => {
  try {
    await signOut()
    router.push('/')
    mobileMenuOpen.value = false
  } catch (error) {
    console.error('Logout error:', error)
  }
}

// User menu items
const userMenuItems = computed(() => {
  const items: any[] = []
  
  // Role-specific menu items
  const roleItems: any[] = []
  if (userRole.value === 'parent') {
    roleItems.push({
      label: 'Dashboard',
      icon: 'i-heroicons-squares-2x2',
      to: '/parent/dashboard'
    })
  } else if (userRole.value === 'student') {
    roleItems.push({
      label: 'My Progress',
      icon: 'i-heroicons-chart-bar',
      to: '/student/dashboard'
    })
  } else if (userRole.value === 'teacher') {
    roleItems.push({
      label: 'Dashboard',
      icon: 'i-heroicons-squares-2x2',
      to: '/dashboard'
    })
  }
  
  if (roleItems.length > 0) {
    items.push(roleItems)
  }
  
  // Logout item
  items.push([{
    label: 'Logout',
    icon: 'i-heroicons-arrow-right-on-rectangle',
    onSelect: handleLogout
  }])
  
  return items
})

// Close mobile menu on route change
watch(() => useRoute().path, () => {
  mobileMenuOpen.value = false
})
</script>

