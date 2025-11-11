export default defineAppConfig({
  ui: {
    input: {
      slots: {
        base: [
          'w-full rounded-md border-0 appearance-none placeholder:text-gray-600 focus:outline-none disabled:cursor-not-allowed disabled:opacity-75',
          'transition-colors'
        ]
      }
    },
    textarea: {
      slots: {
        base: [
          'w-full rounded-md border-0 appearance-none placeholder:text-gray-600 focus:outline-none disabled:cursor-not-allowed disabled:opacity-75',
          'transition-colors'
        ]
      }
    },
    button: {
      compoundVariants: [
        {
          color: 'neutral',
          variant: 'ghost',
          class: {
            base: 'text-gray-700 hover:bg-gray-100 active:bg-gray-100 focus:outline-none focus-visible:bg-gray-100 disabled:bg-transparent'
          }
        },
        {
          color: 'neutral',
          variant: 'outline',
          class: {
            base: 'ring ring-inset ring-gray-300 text-gray-700 hover:bg-gray-50 active:bg-gray-50 disabled:bg-transparent focus:outline-none focus-visible:ring-2 focus-visible:ring-gray-400'
          }
        }
      ]
    }
  }
})

