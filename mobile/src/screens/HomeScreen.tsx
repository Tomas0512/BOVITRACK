import { useMemo } from 'react';
import { ScrollView, View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { AuthStackParamList } from '../navigation/AuthNavigator';
import { useTheme } from '../theme/ThemeContext';

type Nav = NativeStackNavigationProp<AuthStackParamList, 'Home'>;

const features = [
  { icon: '🏡', title: 'Gestion de Fincas', desc: 'Registra y administra tus fincas con ubicacion, extension y proposito productivo.' },
  { icon: '🐂', title: 'Control del Hato', desc: 'Registro completo de cada bovino: identificacion, peso, genealogia y estado reproductivo.' },
  { icon: '🥛', title: 'Produccion Lechera', desc: 'Registra ordenos diarios, consulta promedios y detecta cambios en la produccion.' },
  { icon: '💊', title: 'Sanidad y Tratamientos', desc: 'Controla vacunas, desparasitaciones y tratamientos con fechas de proxima aplicacion.' },
];

const steps = [
  { number: '1', title: 'Crea tu cuenta', desc: 'Registrate en menos de un minuto con tus datos basicos.' },
  { number: '2', title: 'Registra tu finca', desc: 'Agrega tus fincas con ubicacion, extension y proposito productivo.' },
  { number: '3', title: 'Gestiona tu ganado', desc: 'Controla tu hato, produccion, sanidad y tareas desde un solo lugar.' },
];

export default function HomeScreen() {
  const navigation = useNavigation<Nav>();
  const { colors, toggleTheme, isDark } = useTheme();

  const styles = useMemo(() => makeStyles(colors), [colors]);

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <View style={styles.headerRow}>
        <View />
        <TouchableOpacity onPress={toggleTheme} style={styles.themeBtn}>
          <Text style={styles.themeBtnText}>{isDark ? '☀️' : '🌙'}</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.hero}>
        <View style={styles.badge}>
          <Text style={styles.badgeText}>Plataforma de gestion ganadera</Text>
        </View>
        <Text style={styles.heroTitle}>
          Tu ganado bajo control con <Text style={styles.heroTitleAccent}>BoviTrack</Text>
        </Text>
        <Text style={styles.heroSubtitle}>
          La herramienta integral para ganaderos colombianos.
        </Text>
        <TouchableOpacity style={styles.btnPrimary} onPress={() => navigation.navigate('Register')}>
          <Text style={styles.btnPrimaryText}>Comenzar gratis</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.btnSecondary} onPress={() => navigation.navigate('Login')}>
          <Text style={styles.btnSecondaryText}>Ya tengo cuenta</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Todo lo que necesitas</Text>
        <Text style={styles.sectionSubtitle}>Modulos diseñados para cada aspecto de la operacion ganadera.</Text>
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

      <View style={[styles.section, styles.sectionAlt]}>
        <Text style={styles.sectionTitle}>Empieza en 3 pasos</Text>
        <Text style={styles.sectionSubtitle}>Sin configuraciones complicadas.</Text>
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

const makeStyles = (colors: ReturnType<typeof useTheme>['colors']) => StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  content: { paddingBottom: 48 },
  headerRow: { flexDirection: 'row', justifyContent: 'flex-end', padding: 16, paddingTop: 48 },
  themeBtn: { padding: 8 },
  themeBtnText: { fontSize: 22 },
  hero: { padding: 28, alignItems: 'center' },
  badge: {
    backgroundColor: colors.primary + '18',
    borderRadius: 20, paddingHorizontal: 14, paddingVertical: 6, marginBottom: 16,
  },
  badgeText: { color: colors.primary, fontWeight: '600', fontSize: 13 },
  heroTitle: {
    fontSize: 28, fontWeight: '800', color: colors.textPrimary,
    textAlign: 'center', lineHeight: 36, marginBottom: 12,
  },
  heroTitleAccent: { color: colors.primary },
  heroSubtitle: {
    fontSize: 14, color: colors.textSecondary, textAlign: 'center',
    lineHeight: 22, marginBottom: 28,
  },
  btnPrimary: {
    backgroundColor: colors.primary, borderRadius: 12,
    paddingVertical: 15, paddingHorizontal: 32,
    alignItems: 'center', width: '100%', marginBottom: 12,
  },
  btnPrimaryText: { color: colors.textOnPrimary, fontWeight: '700', fontSize: 16 },
  btnSecondary: {
    borderWidth: 2, borderColor: colors.primary, borderRadius: 12,
    paddingVertical: 15, paddingHorizontal: 32,
    alignItems: 'center', width: '100%',
  },
  btnSecondaryText: { color: colors.primary, fontWeight: '700', fontSize: 16 },
  section: { paddingHorizontal: 20, paddingVertical: 32 },
  sectionAlt: { backgroundColor: colors.surfaceAlt },
  sectionTitle: {
    fontSize: 22, fontWeight: '800', color: colors.textPrimary,
    textAlign: 'center', marginBottom: 8,
  },
  sectionSubtitle: {
    fontSize: 13, color: colors.textSecondary, textAlign: 'center',
    lineHeight: 20, marginBottom: 24,
  },
  grid: { flexDirection: 'row', flexWrap: 'wrap', gap: 12 },
  card: {
    width: '47%', backgroundColor: colors.surface, borderRadius: 14,
    padding: 16, borderWidth: 1, borderColor: colors.border,
    shadowColor: '#000', shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.06, shadowRadius: 4, elevation: 2,
  },
  cardIcon: { fontSize: 28, marginBottom: 8 },
  cardTitle: { fontSize: 13, fontWeight: '700', color: colors.textPrimary, marginBottom: 4 },
  cardDesc: { fontSize: 11, color: colors.textMuted, lineHeight: 16 },
  step: { flexDirection: 'row', alignItems: 'flex-start', marginBottom: 20 },
  stepNumber: {
    width: 36, height: 36, borderRadius: 18,
    backgroundColor: colors.primary, alignItems: 'center', justifyContent: 'center',
    marginRight: 14, marginTop: 2,
  },
  stepNumberText: { color: colors.textOnPrimary, fontWeight: '800', fontSize: 15 },
  stepContent: { flex: 1 },
  stepTitle: { fontSize: 15, fontWeight: '700', color: colors.textPrimary, marginBottom: 3 },
  stepDesc: { fontSize: 13, color: colors.textSecondary, lineHeight: 20 },
});
