import { useState, useMemo } from 'react';
import {
  View, Text, TextInput, TouchableOpacity, StyleSheet,
  ActivityIndicator, KeyboardAvoidingView, Platform, ScrollView,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { useMutation } from '@tanstack/react-query';
import { registerUser, getMe } from '../../services/auth';
import { setAuthToken } from '../../services/api';
import { useAuthStore } from '../../store/authStore';
import { AuthStackParamList } from '../../navigation/AuthNavigator';
import { useTheme } from '../../theme/ThemeContext';

type Nav = NativeStackNavigationProp<AuthStackParamList, 'Register'>;
type DocType = 'CC' | 'CE' | 'TI' | 'PP' | 'NIT';
const DOC_TYPES: DocType[] = ['CC', 'CE', 'TI', 'PP', 'NIT'];
const TEXT_ONLY = /^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+$/;

export default function RegisterScreen() {
  const navigation = useNavigation<Nav>();
  const login = useAuthStore((s) => s.login);
  const { colors, toggleTheme, isDark } = useTheme();

  const [form, setForm] = useState({
    email: '', first_name: '', last_name: '',
    document_type: 'CC' as DocType, document_number: '',
    phone: '', password: '', confirmPassword: '',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [serverError, setServerError] = useState('');

  const set = (key: string, value: string) => {
    setForm((prev) => ({ ...prev, [key]: value }));
    if (errors[key]) setErrors((prev) => { const c = { ...prev }; delete c[key]; return c; });
  };

  const validate = () => {
    const e: Record<string, string> = {};
    if (!form.first_name.trim()) e.first_name = 'Los nombres son obligatorios';
    else if (!TEXT_ONLY.test(form.first_name)) e.first_name = 'Solo se permiten letras';
    if (!form.last_name.trim()) e.last_name = 'Los apellidos son obligatorios';
    else if (!TEXT_ONLY.test(form.last_name)) e.last_name = 'Solo se permiten letras';
    if (!form.email.trim()) e.email = 'El correo es obligatorio';
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) e.email = 'Correo invalido';
    if (!form.document_number.trim()) e.document_number = 'El numero es obligatorio';
    if (!form.phone.trim()) e.phone = 'El telefono es obligatorio';
    if (!form.password) e.password = 'La contrasena es obligatoria';
    else if (form.password.length < 8) e.password = 'Minimo 8 caracteres';
    else if (!/[A-Z]/.test(form.password)) e.password = 'Debe tener una mayuscula';
    else if (!/[a-z]/.test(form.password)) e.password = 'Debe tener una minuscula';
    else if (!/\d/.test(form.password)) e.password = 'Debe tener un numero';
    else if (!/[^A-Za-z0-9]/.test(form.password)) e.password = 'Debe tener un caracter especial';
    if (!form.confirmPassword) e.confirmPassword = 'Debe verificar la contrasena';
    else if (form.password !== form.confirmPassword) e.confirmPassword = 'Las contrasenas no coinciden';
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const mutation = useMutation({
    mutationFn: async () => {
      if (!validate()) return Promise.reject(null);
      const tokens = await registerUser({ ...form, accept_terms: true, accept_data_policy: true });
      setAuthToken(tokens.access_token);
      const user = await getMe();
      return { tokens, user };
    },
    onSuccess: ({ tokens, user }) => login(tokens, user),
    onError: (e: Error) => {
      if (e) setServerError(e.message || 'No se pudo registrar');
    },
  });

  const styles = useMemo(() => makeStyles(colors), [colors]);

  const fields = [
    { label: 'Nombre', key: 'first_name', placeholder: 'Juan', keyboard: 'default' as const },
    { label: 'Apellido', key: 'last_name', placeholder: 'Perez', keyboard: 'default' as const },
    { label: 'Correo electronico', key: 'email', placeholder: 'correo@ejemplo.com', keyboard: 'email-address' as const },
    { label: 'Numero de documento', key: 'document_number', placeholder: '1234567890', keyboard: 'numeric' as const },
    { label: 'Telefono', key: 'phone', placeholder: '3001234567', keyboard: 'phone-pad' as const },
  ];

  return (
    <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
      <ScrollView style={styles.container} contentContainerStyle={styles.content}>
        <View style={styles.headerRow}>
          <Text style={styles.title}>Crear cuenta</Text>
          <TouchableOpacity onPress={toggleTheme} style={styles.themeToggle}>
            <Text style={styles.themeToggleText}>{isDark ? '☀️' : '🌙'}</Text>
          </TouchableOpacity>
        </View>
        <Text style={styles.subtitle}>Completa tus datos</Text>

        {serverError ? (
          <View style={styles.errorBanner}>
            <Text style={styles.errorBannerText}>{serverError}</Text>
          </View>
        ) : null}

        {fields.map(({ label, key, placeholder, keyboard }) => (
          <View key={key}>
            <Text style={styles.label}>{label}</Text>
            <TextInput
              style={[styles.input, errors[key] ? styles.inputError : null]}
              value={(form as any)[key]}
              onChangeText={(v) => set(key, v)}
              placeholder={placeholder}
              placeholderTextColor={colors.textMuted}
              keyboardType={keyboard}
              autoCapitalize="none"
            />
            {errors[key] ? <Text style={styles.errorText}>{errors[key]}</Text> : null}
          </View>
        ))}

        <Text style={styles.label}>Tipo de documento</Text>
        <View style={styles.docTypes}>
          {DOC_TYPES.map((type) => (
            <TouchableOpacity
              key={type}
              style={[styles.docChip, form.document_type === type && styles.docChipActive]}
              onPress={() => setForm((p) => ({ ...p, document_type: type }))}
            >
              <Text style={[styles.docChipText, form.document_type === type && styles.docChipTextActive]}>
                {type}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        <Text style={styles.label}>Contrasena</Text>
        <TextInput
          style={[styles.input, errors.password ? styles.inputError : null]}
          value={form.password}
          onChangeText={(v) => set('password', v)}
          secureTextEntry placeholder="Min. 8 caracteres"
          placeholderTextColor={colors.textMuted}
        />
        {errors.password ? <Text style={styles.errorText}>{errors.password}</Text> : null}

        <Text style={styles.label}>Confirmar contrasena</Text>
        <TextInput
          style={[styles.input, errors.confirmPassword ? styles.inputError : null]}
          value={form.confirmPassword}
          onChangeText={(v) => set('confirmPassword', v)}
          secureTextEntry placeholder="Repite la contrasena"
          placeholderTextColor={colors.textMuted}
        />
        {errors.confirmPassword ? <Text style={styles.errorText}>{errors.confirmPassword}</Text> : null}

        <TouchableOpacity
          style={[styles.btnPrimary, mutation.isPending && styles.btnDisabled]}
          onPress={() => mutation.mutate()}
          disabled={mutation.isPending}
        >
          {mutation.isPending
            ? <ActivityIndicator color={colors.textOnPrimary} />
            : <Text style={styles.btnPrimaryText}>Registrarme</Text>}
        </TouchableOpacity>

        <TouchableOpacity onPress={() => navigation.navigate('Login')}>
          <Text style={styles.linkCenter}>
            Ya tienes cuenta? <Text style={styles.linkBold}>Inicia sesion</Text>
          </Text>
        </TouchableOpacity>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const makeStyles = (colors: ReturnType<typeof useTheme>['colors']) => StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  content: { padding: 24, paddingTop: 64 },
  headerRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  themeToggle: { padding: 8 },
  themeToggleText: { fontSize: 22 },
  title: { fontSize: 28, fontWeight: 'bold', color: colors.primaryDark, marginBottom: 4 },
  subtitle: { fontSize: 15, color: colors.textSecondary, marginBottom: 32 },
  label: { fontSize: 14, fontWeight: '600', color: colors.textPrimary, marginBottom: 6 },
  input: {
    borderWidth: 1, borderColor: colors.border, borderRadius: 10,
    padding: 14, fontSize: 15, color: colors.textPrimary,
    backgroundColor: colors.surface, marginBottom: 4,
  },
  inputError: { borderColor: colors.error },
  errorText: { color: colors.error, fontSize: 12, marginBottom: 12, marginLeft: 4 },
  errorBanner: {
    backgroundColor: colors.errorLight, borderRadius: 8,
    padding: 12, marginBottom: 16,
  },
  errorBannerText: { color: colors.error, fontSize: 13, textAlign: 'center' },
  docTypes: { flexDirection: 'row', gap: 8, marginBottom: 16, flexWrap: 'wrap' },
  docChip: {
    borderWidth: 1, borderColor: colors.border, borderRadius: 8,
    paddingHorizontal: 16, paddingVertical: 8,
  },
  docChipActive: { backgroundColor: colors.primary, borderColor: colors.primary },
  docChipText: { color: colors.textSecondary, fontWeight: '600' },
  docChipTextActive: { color: colors.textOnPrimary },
  btnPrimary: {
    backgroundColor: colors.primary, borderRadius: 10,
    padding: 16, alignItems: 'center', marginBottom: 16, marginTop: 8,
  },
  btnDisabled: { opacity: 0.6 },
  btnPrimaryText: { color: colors.textOnPrimary, fontWeight: '700', fontSize: 16 },
  linkCenter: { textAlign: 'center', color: colors.textSecondary, fontSize: 14 },
  linkBold: { color: colors.primary, fontWeight: '700' },
});
