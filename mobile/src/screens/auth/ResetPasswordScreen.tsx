import { useState, useMemo } from 'react';
import {
  View, Text, TextInput, TouchableOpacity, StyleSheet,
  ActivityIndicator, KeyboardAvoidingView, Platform, ScrollView,
} from 'react-native';
import { useNavigation, useRoute, RouteProp } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { useMutation } from '@tanstack/react-query';
import { resetPassword } from '../../services/auth';
import { AuthStackParamList } from '../../navigation/AuthNavigator';
import { useTheme } from '../../theme/ThemeContext';

type Nav = NativeStackNavigationProp<AuthStackParamList, 'ResetPassword'>;
type Route = RouteProp<AuthStackParamList, 'ResetPassword'>;

const validatePassword = (pwd: string): string | null => {
  if (pwd.length < 8) return 'Minimo 8 caracteres';
  if (!/[A-Z]/.test(pwd)) return 'Debe tener una mayuscula';
  if (!/[a-z]/.test(pwd)) return 'Debe tener una minuscula';
  if (!/[0-9]/.test(pwd)) return 'Debe tener un numero';
  if (!/[^A-Za-z0-9]/.test(pwd)) return 'Debe tener un caracter especial';
  return null;
};

export default function ResetPasswordScreen() {
  const navigation = useNavigation<Nav>();
  const route = useRoute<Route>();
  const { token } = route.params;
  const { colors } = useTheme();

  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [done, setDone] = useState(false);
  const [error, setError] = useState('');

  const mutation = useMutation({
    mutationFn: () => {
      const pwdErr = validatePassword(password);
      if (pwdErr) return Promise.reject(new Error(pwdErr));
      if (password !== confirm) return Promise.reject(new Error('Las contrasenas no coinciden'));
      return resetPassword(token, password);
    },
    onSuccess: () => setDone(true),
    onError: (e: Error) => setError(e.message),
  });

  const styles = useMemo(() => makeStyles(colors), [colors]);

  if (done) {
    return (
      <View style={[styles.container, styles.center]}>
        <Text style={{ fontSize: 56, marginBottom: 16 }}>✅</Text>
        <Text style={styles.title}>Contrasena actualizada</Text>
        <Text style={styles.subtitle}>Ya puedes iniciar sesion con tu nueva contrasena.</Text>
        <TouchableOpacity style={styles.btnPrimary} onPress={() => navigation.navigate('Login')}>
          <Text style={styles.btnPrimaryText}>Ir al login</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
      <ScrollView style={styles.container} contentContainerStyle={styles.content}>
        <Text style={styles.title}>Nueva contrasena</Text>
        <Text style={styles.subtitle}>Min. 8 caracteres, una mayuscula, una minuscula y un numero.</Text>

        {error ? (
          <View style={styles.errorBanner}>
            <Text style={styles.errorBannerText}>{error}</Text>
          </View>
        ) : null}

        <Text style={styles.label}>Nueva contrasena</Text>
        <TextInput
          style={[styles.input, error ? styles.inputError : null]}
          value={password} onChangeText={(v) => { setPassword(v); setError(''); }}
          secureTextEntry placeholder="********" placeholderTextColor={colors.textMuted}
        />

        <Text style={styles.label}>Confirmar contrasena</Text>
        <TextInput
          style={[styles.input, error ? styles.inputError : null]}
          value={confirm} onChangeText={(v) => { setConfirm(v); setError(''); }}
          secureTextEntry placeholder="********" placeholderTextColor={colors.textMuted}
        />

        <TouchableOpacity
          style={[styles.btnPrimary, mutation.isPending && styles.btnDisabled]}
          onPress={() => mutation.mutate()}
          disabled={mutation.isPending}
        >
          {mutation.isPending
            ? <ActivityIndicator color={colors.textOnPrimary} />
            : <Text style={styles.btnPrimaryText}>Cambiar contrasena</Text>}
        </TouchableOpacity>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const makeStyles = (colors: ReturnType<typeof useTheme>['colors']) => StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  content: { padding: 24, paddingTop: 64 },
  center: { justifyContent: 'center', alignItems: 'center', padding: 32 },
  title: { fontSize: 28, fontWeight: 'bold', color: colors.primaryDark, marginBottom: 8 },
  subtitle: { fontSize: 15, color: colors.textSecondary, marginBottom: 32 },
  label: { fontSize: 14, fontWeight: '600', color: colors.textPrimary, marginBottom: 6 },
  input: {
    borderWidth: 1, borderColor: colors.border, borderRadius: 10,
    padding: 14, fontSize: 15, color: colors.textPrimary,
    backgroundColor: colors.surface, marginBottom: 16,
  },
  inputError: { borderColor: colors.error },
  errorBanner: {
    backgroundColor: colors.errorLight, borderRadius: 8,
    padding: 12, marginBottom: 16,
  },
  errorBannerText: { color: colors.error, fontSize: 13, textAlign: 'center' },
  btnPrimary: {
    backgroundColor: colors.primary, borderRadius: 10,
    padding: 16, alignItems: 'center', marginTop: 8,
  },
  btnDisabled: { opacity: 0.6 },
  btnPrimaryText: { color: colors.textOnPrimary, fontWeight: '700', fontSize: 16 },
});
