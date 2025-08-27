export function Card({ children, className = "" }) {
    return (
      <div
        className={`border border-black rounded-lg bg-black shadow-sm text-white ${className}`}
        style={{ borderColor: '#111' }} // explicit darker border color
      >
        {children}
      </div>
    );
  }
  
  
  export function CardContent({ children, className = "" }) {
    return <div className={`p-6 ${className}`}>{children}</div>;
  }
  