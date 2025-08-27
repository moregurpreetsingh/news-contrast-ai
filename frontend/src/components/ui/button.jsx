// src/components/ui/button.jsx

export function Button({ children, className = '', type = 'button', ...props }) {
    return (
      <button
        type={type}
        className={`
          inline-flex items-center justify-center 
          rounded-md text-sm font-medium 
          px-4 py-2 
          bg-primary text-primary-foreground 
          hover:bg-primary/90 
          transition-colors
          focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 
          disabled:opacity-50 disabled:pointer-events-none
          ${className}
        `}
        {...props}
      >
        {children}
      </button>
    )
  }
  