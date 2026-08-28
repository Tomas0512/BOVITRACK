import { useEffect } from 'react';
import { useAuthStore } from '../store/authStore';
import AuthNavigator from './AuthNavigator';
import AppNavigator from './AppNavigator';

export default function RootNavigator() {
  const accessToken = useAuthStore((s) => s.accessToken);
  const loading = useAuthStore((s) => s.loading);
  const hydrate = useAuthStore((s) => s.hydrate);

  useEffect(() => {
    void hydrate();
  }, [hydrate]);

  if (loading) return null;

  return accessToken ? <AppNavigator /> : <AuthNavigator />;
}
