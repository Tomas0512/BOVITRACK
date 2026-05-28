import { useAuthStore } from '../store/authStore';
import AuthNavigator from './AuthNavigator';
import AppNavigator from './AppNavigator';

export default function RootNavigator() {
  const accessToken = useAuthStore((state) => state.accessToken);
  return accessToken ? <AppNavigator /> : <AuthNavigator />;
}