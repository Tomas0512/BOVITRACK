import { View, Text, StyleSheet, ScrollView, ActivityIndicator, TouchableOpacity } from 'react-native';
import { useRoute, useNavigation, RouteProp } from '@react-navigation/native';
import { useQuery } from '@tanstack/react-query';
import { getFarm } from '../services/farms';
import { AppStackParamList } from '../navigation/AppNavigator';
import { colors } from '../theme/colors';

type Route = RouteProp<AppStackParamList, 'FarmDetail'>;

export default function FarmDetailScreen() {
  const { params } = useRoute<Route>();
  const navigation = useNavigation();

  const { data: farm, isLoading, isError } = useQuery({
    queryKey: ['farm', params.farmId],
    queryFn: () => getFarm(params.farmId),
  });

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Text style={styles.back}>← Volver</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Detalle de finca</Text>
        <View style={{ width: 60 }} />
      </View>

      {isLoading && (
        <View style={styles.center}>
          <ActivityIndicator size="large" color={colors.primary} />
        </View>
      )}

      {isError && (
        <View style={styles.center}>
          <Text style={styles.errorText}>No se pudo cargar la finca</Text>
        </View>
      )}

      {farm && (
        <ScrollView contentContainerStyle={styles.content}>
          <View style={styles.card}>
            <Text style={styles.farmName}>{farm.name}</Text>
            {farm.purpose && (
              <View style={styles.badge}>
                <Text style={styles.badgeText}>{farm.purpose}</Text>
              </View>
            )}
          </View>

          <View style={styles.infoCard}>
            <Text style={styles.infoTitle}>Información general</Text>
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>📍 Ubicación</Text>
              <Text style={styles.infoValue}>{farm.city}, {farm.department}</Text>
            </View>
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>🏠 Dirección</Text>
              <Text style={styles.infoValue}>{farm.address}</Text>
            </View>
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>📐 Extensión</Text>
              <Text style={styles.infoValue}>{farm.hectares} hectáreas</Text>
            </View>
          </View>
        </ScrollView>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F9FAF8' },
  header: {
    flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center',
    paddingHorizontal: 16, paddingTop: 52, paddingBottom: 16,
    backgroundColor: '#fff', borderBottomWidth: 1, borderBottomColor: '#F3F4F6',
  },
  back: { color: colors.primary, fontSize: 15, fontWeight: '600', width: 60 },
  headerTitle: { fontSize: 17, fontWeight: '700', color: '#111827' },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  errorText: { color: '#EF4444', fontSize: 15 },
  content: { padding: 16, gap: 12 },
  card: {
    backgroundColor: '#fff', borderRadius: 14, padding: 20,
    borderWidth: 1, borderColor: '#F3F4F6',
  },
  farmName: { fontSize: 22, fontWeight: '800', color: '#111827', marginBottom: 8 },
  badge: {
    alignSelf: 'flex-start', backgroundColor: colors.primary + '18',
    borderRadius: 20, paddingHorizontal: 12, paddingVertical: 4,
  },
  badgeText: { color: colors.primary, fontWeight: '600', fontSize: 12 },
  infoCard: {
    backgroundColor: '#fff', borderRadius: 14, padding: 16,
    borderWidth: 1, borderColor: '#F3F4F6',
  },
  infoTitle: { fontSize: 15, fontWeight: '700', color: '#111827', marginBottom: 12 },
  infoRow: {
    flexDirection: 'row', justifyContent: 'space-between',
    paddingVertical: 8, borderBottomWidth: 1, borderBottomColor: '#F9FAF8',
  },
  infoLabel: { fontSize: 13, color: '#6B7280' },
  infoValue: { fontSize: 13, color: '#111827', fontWeight: '500', flex: 1, textAlign: 'right' },
});