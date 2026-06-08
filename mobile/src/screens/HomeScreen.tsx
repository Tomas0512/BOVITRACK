import { ScrollView, View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { AuthStackParamList } from '../navigation/AuthNavigator';
import { colors } from '../theme/colors';

type Nav = NativeStackNavigationProp<AuthStackParamList, 'Home'>;

const features = [
  {
    icon: '🏡',
    title: 'Gestión de Fincas',
    desc: 'Registra y administra tus fincas con ubicación, extensión y propósito productivo.',
  },
  {
    icon: '🐂',
    title: 'Control del Hato',
    desc: 'Registro completo de cada bovino: identificación, peso, genealogía y estado reproductivo.',
  },
  {
    icon: '🥛',
    title: 'Producción Lechera',
    desc: 'Registra ordeños diarios, consulta promedios y detecta cambios en la producción.',
  },
  {
    icon: '💊',
    title: 'Sanidad y Tratamientos',
    desc: 'Controla vacunas, desparasitaciones y tratamientos con fechas de próxima aplicación.',
  },
];

const steps = [
  { number: '1', title: 'Crea tu cuenta', desc: 'Regístrate en menos de un minuto con tus datos básicos.' },
  { number: '2', title: 'Registra tu finca', desc: 'Agrega tus fincas con ubicación, extensión y propósito productivo.' },
  { number: '3', title: 'Gestiona tu ganado', desc: 'Controla tu hato, producción, sanidad y tareas desde un solo lugar.' },
];

export default function HomeScreen() {
  const navigation = useNavigation<Nav>();

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>

      {/* ── Hero ── */}
      <View style={styles.hero}>
        <View style={styles.badge}>
          <Text style={styles.badgeText}>Plataforma de gestión ganadera</Text>
        </View>
        <Text style={styles.heroTitle}>Tu ganado bajo control con{' '}
          <Text style={styles.heroTitleAccent}>BoviTrack</Text>
        </Text>
        <Text style={styles.heroSubtitle}>
          La herramienta integral para ganaderos colombianos. Registra fincas, controla tu hato,
          producción lechera, tratamientos y tareas — todo desde un solo lugar.
        </Text>
        <TouchableOpacity style={styles.btnPrimary} onPress={() => navigation.navigate('Register')}>
          <Text style={styles.btnPrimaryText}>Comenzar gratis</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.btnSecondary} onPress={() => navigation.navigate('Login')}>
          <Text style={styles.btnSecondaryText}>Ya tengo cuenta</Text>
        </TouchableOpacity>
      </View>

      {/* ── Características ── */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Todo lo que necesitas</Text>
        <Text style={styles.sectionSubtitle}>
          Módulos diseñados para cubrir cada aspecto de la operación ganadera diaria.
        </Text>
        <View style={styles.grid}>
          {features.map((f) => (
            <View key={f.title} style={styles.card}>
              <Text style={styles.cardIcon}>{f.icon}</Text>
              <Text style={styles.cardTitle}>{f.title}</Text>
              <Text style={styles.cardDesc}>{f.desc}</Text>
            </View>
          ))}
        </View>
      </View>

      {/* ── Cómo funciona ── */}
      <View style={[styles.section, styles.sectionAlt]}>
        <Text style={styles.sectionTitle}>Empieza en 3 pasos</Text>
        <Text style={styles.sectionSubtitle}>
          Sin configuraciones complicadas. Registra, configura y gestiona.
        </Text>
        {steps.map((s) => (
          <View key={s.number} style={styles.step}>
            <View style={styles.stepNumber}>
              <Text style={styles.stepNumberText}>{s.number}</Text>
            </View>
            <View style={styles.stepContent}>
              <Text style={styles.stepTitle}>{s.title}</Text>
              <Text style={styles.stepDesc}>{s.desc}</Text>
            </View>
          </View>
        ))}
      </View>

    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  content: { paddingBottom: 48 },

  // Hero
  hero: { padding: 28, paddingTop: 56, alignItems: 'center' },
  badge: {
    backgroundColor: colors.primary + '18',
    borderRadius: 20, paddingHorizontal: 14, paddingVertical: 6, marginBottom: 16,
  },
  badgeText: { color: colors.primary, fontWeight: '600', fontSize: 13 },
  heroTitle: {
    fontSize: 28, fontWeight: '800', color: '#111827',
    textAlign: 'center', lineHeight: 36, marginBottom: 12,
  },
  heroTitleAccent: { color: colors.primary },
  heroSubtitle: {
    fontSize: 14, color: '#6B7280', textAlign: 'center',
    lineHeight: 22, marginBottom: 28,
  },
  btnPrimary: {
    backgroundColor: colors.primary, borderRadius: 12,
    paddingVertical: 15, paddingHorizontal: 32,
    alignItems: 'center', width: '100%', marginBottom: 12,
  },
  btnPrimaryText: { color: '#fff', fontWeight: '700', fontSize: 16 },
  btnSecondary: {
    borderWidth: 2, borderColor: colors.primary, borderRadius: 12,
    paddingVertical: 15, paddingHorizontal: 32,
    alignItems: 'center', width: '100%',
  },
  btnSecondaryText: { color: colors.primary, fontWeight: '700', fontSize: 16 },

  // Sections
  section: { paddingHorizontal: 20, paddingVertical: 32 },
  sectionAlt: { backgroundColor: '#F9FAF8' },
  sectionTitle: {
    fontSize: 22, fontWeight: '800', color: '#111827',
    textAlign: 'center', marginBottom: 8,
  },
  sectionSubtitle: {
    fontSize: 13, color: '#6B7280', textAlign: 'center',
    lineHeight: 20, marginBottom: 24,
  },

  // Features grid
  grid: { flexDirection: 'row', flexWrap: 'wrap', gap: 12 },
  card: {
    width: '47%', backgroundColor: '#fff', borderRadius: 14,
    padding: 16, borderWidth: 1, borderColor: '#F3F4F6',
    shadowColor: '#000', shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.06, shadowRadius: 4, elevation: 2,
  },
  cardIcon: { fontSize: 28, marginBottom: 8 },
  cardTitle: { fontSize: 13, fontWeight: '700', color: '#111827', marginBottom: 4 },
  cardDesc: { fontSize: 11, color: '#9CA3AF', lineHeight: 16 },

  // Steps
  step: { flexDirection: 'row', alignItems: 'flex-start', marginBottom: 20 },
  stepNumber: {
    width: 36, height: 36, borderRadius: 18,
    backgroundColor: colors.primary, alignItems: 'center', justifyContent: 'center',
    marginRight: 14, marginTop: 2,
  },
  stepNumberText: { color: '#fff', fontWeight: '800', fontSize: 15 },
  stepContent: { flex: 1 },
  stepTitle: { fontSize: 15, fontWeight: '700', color: '#111827', marginBottom: 3 },
  stepDesc: { fontSize: 13, color: '#6B7280', lineHeight: 20 },
});