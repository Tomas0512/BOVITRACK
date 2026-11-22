import { Navigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import type { ReactNode } from "react";

interface Props {
  role: string;
  children: ReactNode;
}

/**
 * Guard que solo permite renderizar el contenido si el rol del usuario en sesión
 * coincide con el indicado; de lo contrario redirige al dashboard.
 */
export default function RequireRole({ role, children }: Props) {
  const { user } = useAuth();
  if (user?.role_name !== role) {
    return <Navigate to="/dashboard" replace />;
  }
  return <>{children}</>;
}
