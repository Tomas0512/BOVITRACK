import { ScrollView, View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { AuthStackParamList } from '../navigation/AuthNavigator';
import { colors } from '../theme/colors';

type Nav = NativeStackNavigationProp<AuthStackParamList, 'Home'>;

const features = [
  { icon: '🏡', title: 'Gestión Fincas', desc: 'Administra tus fincas' },
  { icon: '🐂', title: 'Control Hato', desc: 'Registra tu ganado' },
  { icon: '🥛', title: 'Producción Lechera', desc: 'Monitorea producción' },
  { icon: '💉', title: 'Sanidad', desc: 'Control de tratamientos' },
];

export default function HomeScreen() {
  const navigation = useNavigation<Nav>();

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <View style={styles.hero}>
        <Text style={styles.title}>🐄 Bovitrack</Text>
        <Text style={styles.subtitle}>Gestión inteligente de fincas ganaderas</Text>
      </View>

      <View style={styles.grid}>
        {features.map((f) => (
          <View key={f.title} style={styles.card}>
            <Text style={styles.cardIcon}>{f.icon}</Text>
            <Text style={styles.cardTitle}>{f.title}</Text>
            <Text style={styles.cardDesc}>{f.desc}</Text>
          </View>
        ))}
      </View>

      <TouchableOpacity style={styles.btnPrimary} onPress={() => navigation.navigate('Login')}>
        <Text style={styles.btnPrimaryText}>Iniciar sesión</Text>
      </TouchableOpacity>
      <TouchableOpacity style={styles.btnSecondary} onPress={() => navigation.navigate('Register')}>
        <Text style={styles.btnSecondaryText}>Crear cuenta</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  content: { padding: 24, paddingTop: 64 },
  hero: { alignItems: 'center', marginBottom: 32 },
  title: { fontSize: 36, fontWeight: 'bold', color: colors.primaryDark, marginBottom: 8 },
  subtitle: { fontSize: 15, color: colors.textSecondary, textAlign: 'center' },
  grid: { flexDirection: 'row', flexWrap: 'wrap', gap: 12, marginBottom: 32 },
  card: {
    width: '47%', backgroundColor: colors.surface, borderRadius: 12,
    padding: 16, alignItems: 'center',
    shadowColor: '#000', shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.08, shadowRadius: 4, elevation: 2,
  },
  cardIcon: { fontSize: 28, marginBottom: 6 },
  cardTitle: { fontSize: 13, fontWeight: '600', color: colors.textPrimary, marginBottom: 2 },
  cardDesc: { fontSize: 11, color: colors.textMuted, textAlign: 'center' },
  btnPrimary: {
    backgroundColor: colors.primary, borderRadius: 10,
    padding: 16, alignItems: 'center', marginBottom: 12,
  },
  btnPrimaryText: { color: colors.textOnPrimary, fontWeight: '700', fontSize: 16 },
  btnSecondary: {
    borderWidth: 2, borderColor: colors.primary, borderRadius: 10,
    padding: 16, alignItems: 'center', marginBottom: 24,
  },
  btnSecondaryText: { color: colors.primary, fontWeight: '700', fontSize: 16 },
});