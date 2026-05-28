import { useState } from 'react';
import {
  View, Text, TextInput, TouchableOpacity, StyleSheet,
  ActivityIndicator, Alert, KeyboardAvoidingView, Platform, ScrollView,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { useMutation } from '@tanstack/react-query';
import { loginUser, getMe } from '../../services/auth';
import { setAuthToken } from '../../services/api';
import { useAuthStore } from '../../store/authStore';
import { AuthStackParamList } from '../../navigation/AuthNavigator';
import { colors } from '../../theme/colors';

type Nav = NativeStackNavigationProp<AuthStackParamList, 'Login'>;

export default function LoginScreen() {
  const navigation = useNavigation<Nav>();
  const login = useAuthStore((s) => s.login);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const mutation = useMutation({
    mutationFn: async () => {
      const tokens = await loginUser({ email, password });
      setAuthToken(tokens.access_token);
      const user = await getMe();
      return { tokens, user };
    },
    onSuccess: ({ tokens, user }) => login(tokens, user),
    onError: (e: Error) => Alert.alert('Error', e.message || 'Credenciales incorrectas'),
  });

  return (
    <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
      <ScrollView style={styles.container} contentContainerStyle={styles.content}>
        <Text style={styles.title}>Iniciar sesión</Text>
        <Text style={styles.subtitle}>Bienvenido de nuevo</Text>

        <Text style={styles.label}>Correo electrónico</Text>
        <TextInput
          style={styles.input} value={email} onChangeText={setEmail}
          keyboardType="email-address" autoCapitalize="none"
          placeholder="correo@ejemplo.com" placeholderTextColor={colors.textMuted}
        />

        <Text style={styles.label}>Contraseña</Text>
        <TextInput
          style={styles.input} value={password} onChangeText={setPassword}
          secureTextEntry placeholder="••••••••" placeholderTextColor={colors.textMuted}
        />

        <TouchableOpacity onPress={() => navigation.navigate('ForgotPassword')}>
          <Text style={styles.linkRight}>¿Olvidaste tu contraseña?</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.btnPrimary, mutation.isPending && styles.btnDisabled]}
          onPress={() => mutation.mutate()}
          disabled={mutation.isPending}
        >
          {mutation.isPending
            ? <ActivityIndicator color={colors.textOnPrimary} />
            : <Text style={styles.btnPrimaryText}>Ingresar</Text>}
        </TouchableOpacity>

        <TouchableOpacity onPress={() => navigation.navigate('Register')}>
          <Text style={styles.linkCenter}>
            ¿No tienes cuenta? <Text style={styles.linkBold}>Regístrate</Text>
          </Text>
        </TouchableOpacity>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  content: { padding: 24, paddingTop: 64 },
  title: { fontSize: 28, fontWeight: 'bold', color: colors.primaryDark, marginBottom: 4 },
  subtitle: { fontSize: 15, color: colors.textSecondary, marginBottom: 32 },
  label: { fontSize: 14, fontWeight: '600', color: colors.textPrimary, marginBottom: 6 },
  input: {
    borderWidth: 1, borderColor: colors.border, borderRadius: 10,
    padding: 14, fontSize: 15, color: colors.textPrimary,
    backgroundColor: colors.surface, marginBottom: 16,
  },
  linkRight: { color: colors.primary, fontSize: 13, textAlign: 'right', marginBottom: 24 },
  btnPrimary: {
    backgroundColor: colors.primary, borderRadius: 10,
    padding: 16, alignItems: 'center', marginBottom: 16,
  },
  btnDisabled: { opacity: 0.6 },
  btnPrimaryText: { color: colors.textOnPrimary, fontWeight: '700', fontSize: 16 },
  linkCenter: { textAlign: 'center', color: colors.textSecondary, fontSize: 14 },
  linkBold: { color: colors.primary, fontWeight: '700' },
});