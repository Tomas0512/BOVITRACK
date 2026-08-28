import { useMemo } from 'react';
import { View, Text, StyleSheet, ActivityIndicator, TouchableOpacity } from 'react-native';
import { useRoute, RouteProp, useNavigation } from '@react-navigation/native';
import { useQuery } from '@tanstack/react-query';
import { getFarm } from '../services/farms';
import { useTheme } from '../theme/ThemeContext';
import { AppStackParamList } from '../navigation/AppNavigator';

type Route = RouteProp<AppStackParamList, 'FarmDetail'>;

export default function FarmDetailScreen() {
  const route = useRoute<Route>();
  const navigation = useNavigation();
  const { colors } = useTheme();
  const { farmId } = route.params;

  const { data: farm, isLoading, isError } = useQuery({
    queryKey: ['farm', farmId],
    queryFn: () => getFarm(farmId),
  });

  const styles = useMemo(() => makeStyles(colors), [colors]);

  if (isLoading) {
    return (
      <View style={[styles.container, styles.center]}>
        <ActivityIndicator size="large" color={colors.primary} />
      </View>
    );
  }

  if (isError || !farm) {
    return (
      <View style={[styles.container, styles.center]}>
        <Text style={styles.errorText}>Error al cargar finca</Text>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Text style={styles.backLink}>Volver</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>{farm.name}</Text>
        <Text style={styles.subtitle}>{farm.address}</Text>
      </View>
      <View style={styles.content}>
        <Text style={styles.label}>Identificador</Text>
        <Text style={styles.value}>{farm.farm_identifier}</Text>
        <Text style={styles.label}>Ciudad / municipio</Text>
        <Text style={styles.value}>{farm.city_municipality}</Text>
        <Text style={styles.label}>Área</Text>
        <Text style={styles.value}>{farm.total_area} {farm.area_unit}</Text>
      </View>
    </View>
  );
}

const makeStyles = (colors: ReturnType<typeof useTheme>['colors']) => StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  center: { justifyContent: 'center', alignItems: 'center' },
  header: {
    backgroundColor: colors.primary, padding: 24, paddingTop: 56,
  },
  title: { fontSize: 24, fontWeight: 'bold', color: colors.textOnPrimary },
  subtitle: { fontSize: 14, color: colors.cream, marginTop: 4 },
  content: { padding: 24 },
  label: { fontSize: 13, fontWeight: '600', color: colors.textSecondary, marginTop: 16, marginBottom: 2 },
  value: { fontSize: 16, color: colors.textPrimary },
  errorText: { fontSize: 16, color: colors.error, marginBottom: 16 },
  backLink: { color: colors.primary, fontSize: 15, fontWeight: '600' },
});
