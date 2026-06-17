import { useState, useMemo } from 'react';
import {
  View, Text, TextInput, TouchableOpacity, StyleSheet,
  ActivityIndicator, KeyboardAvoidingView, Platform, ScrollView,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { useMutation } from '@tanstack/react-query';
import { loginUser, getMe } from '../../services/auth';
import { setAuthToken } from '../../services/api';
import { useAuthStore } from '../../store/authStore';
import { AuthStackParamList } from '../../navigation/AuthNavigator';
import { useTheme } from '../../theme/ThemeContext';

type Nav = NativeStackNavigationProp<AuthStackParamList, 'Login'>;

export default function LoginScreen() {
  const navigation = useNavigation<Nav>();
  const login = useAuthStore((s) => s.login);
  const { colors, toggleTheme, isDark } = useTheme();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [serverError, setServerError] = useState('');

  const validate = () => {
    const newErrors: Record<string, string> = {};
    if (!email.trim()) newErrors.email = 'El correo es obligatorio';
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) newErrors.email = 'Correo invalido';
    if (!password) newErrors.password = 'La contrasena es obligatoria';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const mutation = useMutation({
    mutationFn: async () => {
      const tokens = await loginUser({ email, password });
      setAuthToken(tokens.access_token);
      const user = await getMe();
      return { tokens, user };
    },
    onSuccess: ({ tokens, user }) => login(tokens, user),
    onError: (e: Error) => setServerError(e.message || 'Credenciales incorrectas'),
  });

  const handleSubmit = () => {
    setServerError('');
    if (validate()) mutation.mutate();
  };

  const styles = useMemo(() => makeStyles(colors), [colors]);

  return (
    <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
      <ScrollView style={styles.container} contentContainerStyle={styles.content}>
        <View style={styles.headerRow}>
          <Text style={styles.title}>Iniciar sesion</Text>
          <TouchableOpacity onPress={toggleTheme} style={styles.themeToggle}>
            <Text style={styles.themeToggleText}>{isDark ? '☀️' : '🌙'}</Text>
          </TouchableOpacity>
        </View>
        <Text style={styles.subtitle}>Bienvenido de nuevo</Text>

        {serverError ? (
          <View style={styles.errorBanner}>
            <Text style={styles.errorBannerText}>{serverError}</Text>
          </View>
        ) : null}

        <Text style={styles.label}>Correo electronico</Text>
        <TextInput
          style={[styles.input, errors.email ? styles.inputError : null]}
          value={email} onChangeText={(v) => { setEmail(v); if (errors.email) setErrors((p) => { const c = { ...p }; delete c.email; return c; }); }}
          keyboardType="email-address" autoCapitalize="none"
          placeholder="correo@ejemplo.com" placeholderTextColor={colors.textMuted}
        />
        {errors.email ? <Text style={styles.errorText}>{errors.email}</Text> : null}

        <Text style={styles.label}>Contrasena</Text>
        <TextInput
          style={[styles.input, errors.password ? styles.inputError : null]}
          value={password} onChangeText={(v) => { setPassword(v); if (errors.password) setErrors((p) => { const c = { ...p }; delete c.password; return c; }); }}
          secureTextEntry placeholder="********" placeholderTextColor={colors.textMuted}
        />
        {errors.password ? <Text style={styles.errorText}>{errors.password}</Text> : null}

        <TouchableOpacity onPress={() => navigation.navigate('ForgotPassword')}>
          <Text style={styles.linkRight}>Olvidaste tu contrasena?</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.btnPrimary, mutation.isPending && styles.btnDisabled]}
          onPress={handleSubmit}
          disabled={mutation.isPending}
        >
          {mutation.isPending
            ? <ActivityIndicator color={colors.textOnPrimary} />
            : <Text style={styles.btnPrimaryText}>Ingresar</Text>}
        </TouchableOpacity>

        <TouchableOpacity onPress={() => navigation.navigate('Register')}>
          <Text style={styles.linkCenter}>
            No tienes cuenta? <Text style={styles.linkBold}>Registrate</Text>
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
  linkRight: { color: colors.primary, fontSize: 13, textAlign: 'right', marginBottom: 24, marginTop: 8 },
  btnPrimary: {
    backgroundColor: colors.primary, borderRadius: 10,
    padding: 16, alignItems: 'center', marginBottom: 16,
  },
  btnDisabled: { opacity: 0.6 },
  btnPrimaryText: { color: colors.textOnPrimary, fontWeight: '700', fontSize: 16 },
  linkCenter: { textAlign: 'center', color: colors.textSecondary, fontSize: 14 },
  linkBold: { color: colors.primary, fontWeight: '700' },
});
