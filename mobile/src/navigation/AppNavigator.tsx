import { createNativeStackNavigator } from '@react-navigation/native-stack';
import DashboardScreen from '../screens/DashboardScreen';
import FarmDetailScreen from '../screens/FarmDetailScreen';

export type AppStackParamList = {
  Dashboard: undefined;
  FarmDetail: { farmId: string };
};

const Stack = createNativeStackNavigator<AppStackParamList>();

export default function AppNavigator() {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="Dashboard" component={DashboardScreen} />
      <Stack.Screen name="FarmDetail" component={FarmDetailScreen} />
    </Stack.Navigator>
  );
}