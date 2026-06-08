import {
  View, Text, FlatList, TouchableOpacity, StyleSheet,
  ActivityIndicator, RefreshControl,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { useQuery } from '@tanstack/react-query';
import { useAuthStore } from '../store/authStore';
import { listFarms } from '../services/farms';
import { FarmResponse } from '../types/farms';
import { colors } from '../theme/colors';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { AppStackParamList } from '../navigation/AppNavigator';

export default function DashboardScreen() {
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);
  const navigation = useNavigation<NativeStackNavigationProp<AppStackParamList>>();

  const { data: farms, isLoading, isError, refetch } = useQuery({
    queryKey: ['farms'],
    queryFn: listFarms,
  });

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <View>
          <Text style={styles.greeting}>¡Hola, {user?.first_name}! 👋</Text>
          <Text style={styles.headerSub}>Tus fincas</Text>
        </View>
        <TouchableOpacity style={styles.logoutBtn} onPress={logout}>
          <Text style={styles.logoutText}>Salir</Text>
        </TouchableOpacity>
      </View>

      {/* States */}
      {isLoading && (
        <View style={styles.center}>
          <ActivityIndicator size="large" color={colors.primary} />
          <Text style={styles.stateText}>Cargando fincas...</Text>
        </View>
      )}

      {isError && (
        <View style={styles.center}>
          <Text style={styles.errorIcon}>⚠️</Text>
          <Text style={styles.stateText}>No se pudieron cargar las fincas</Text>
          <TouchableOpacity style={styles.retryBtn} onPress={() => refetch()}>
            <Text style={styles.retryText}>Reintentar</Text>
          </TouchableOpacity>
        </View>
      )}

      {!isLoading && !isError && farms?.length === 0 && (
        <View style={styles.center}>
          <Text style={styles.emptyIcon}>🏡</Text>
          <Text style={styles.stateText}>Aún no tienes fincas registradas</Text>
        </View>
      )}

      {!isLoading && !isError && farms && farms.length > 0 && (
        <FlatList
          data={farms}
          keyExtractor={(item) => item.id}
          contentContainerStyle={styles.list}
          refreshControl={<RefreshControl refreshing={false} onRefresh={() => refetch()} />}
          renderItem={({ item }: { item: FarmResponse }) => (
  <TouchableOpacity
    style={styles.card}
    onPress={() => navigation.navigate('FarmDetail', { farmId: item.id })}
  >
    <Text style={styles.farmName}>{item.name}</Text>
    <Text style={styles.farmDetail}>📍 {item.city}, {item.department}</Text>
    <Text style={styles.farmDetail}>📐 {item.hectares} hectáreas</Text>
    <Text style={styles.farmArrow}>Ver detalle →</Text>
  </TouchableOpacity>
)}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  header: {
    flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center',
    backgroundColor: colors.primary, padding: 24, paddingTop: 56,
  },
  greeting: { fontSize: 22, fontWeight: 'bold', color: colors.textOnPrimary },
  headerSub: { fontSize: 14, color: colors.secondaryLight, marginTop: 2 },
  logoutBtn: {
    backgroundColor: 'rgba(255,255,255,0.2)', borderRadius: 8,
    paddingHorizontal: 14, paddingVertical: 8,
  },
  logoutText: { color: colors.textOnPrimary, fontWeight: '600' },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 32 },
  stateText: { color: colors.textSecondary, fontSize: 15, marginTop: 12, textAlign: 'center' },
  errorIcon: { fontSize: 40 },
  emptyIcon: { fontSize: 48, marginBottom: 8 },
  retryBtn: {
    marginTop: 16, backgroundColor: colors.primary, borderRadius: 8,
    paddingHorizontal: 24, paddingVertical: 10,
  },
  retryText: { color: colors.textOnPrimary, fontWeight: '600' },
  list: { padding: 16 },
  card: {
    backgroundColor: colors.surface, borderRadius: 12, padding: 16,
    marginBottom: 12, shadowColor: '#000', shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.08, shadowRadius: 4, elevation: 2,
  },
  farmName: { fontSize: 17, fontWeight: '700', color: colors.textPrimary, marginBottom: 6 },
  farmDetail: { fontSize: 13, color: colors.textSecondary, marginBottom: 2 },
  farmArrow: { fontSize: 12, color: colors.primary, fontWeight: '600', marginTop: 8, textAlign: 'right' },
});