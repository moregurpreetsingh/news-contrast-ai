// src/hooks/use-toast.jsx

import { useState, createContext, useContext } from "react";

// The context to manage toast state
const ToastContext = createContext(null);

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  // The toast function that adds a new toast to the state
  const toast = (props) => {
    const id = Date.now();
    setToasts((prev) => [...prev, { id, ...props }]);
    return { id };
  };

  const removeToast = (id) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id));
  };

  return (
    <ToastContext.Provider value={{ toast, removeToast }}>
      {children}
      {/* This part would typically render the actual toast components. */}
      {/* For simplicity, we'll just show a basic version here. */}
      <div style={{ position: "fixed", bottom: "1rem", right: "1rem", zIndex: 1000 }}>
        {toasts.map((t) => (
          <div
            key={t.id}
            style={{
              padding: "1rem",
              margin: "0.5rem 0",
              background: t.variant === "destructive" ? "#fecaca" : "#d1e7dd",
              color: t.variant === "destructive" ? "#991b1b" : "#0f5132",
              border: "1px solid",
              borderRadius: "0.5rem",
              boxShadow: "0 2px 10px rgba(0,0,0,0.1)",
            }}
          >
            <strong>{t.title}</strong>
            <p>{t.description}</p>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

// The hook to use the toast function
export function useToast() {
  const context = useContext(ToastContext);
  if (context === null) {
    throw new Error("useToast must be used within a ToastProvider");
  }
  return context;
}