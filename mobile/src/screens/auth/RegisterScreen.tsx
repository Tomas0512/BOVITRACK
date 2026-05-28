import { useState } from 'react';
import {
  View, Text, TextInput, TouchableOpacity, StyleSheet,
  ActivityIndicator, Alert, KeyboardAvoidingView, Platform, ScrollView,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { useMutation } from '@tanstack/react-query';
import { registerUser, getMe } from '../../services/auth';
import { setAuthToken } from '../../services/api';
import { useAuthStore } from '../../store/authStore';
import { AuthStackParamList } from '../../navigation/AuthNavigator';
import { colors } from '../../theme/colors';

type Nav = NativeStackNavigationProp<AuthStackParamList, 'Register'>;
type DocType = 'CC' | 'CE' | 'TI' | 'PP' | 'NIT';
const DOC_TYPES: DocType[] = ['CC', 'CE', 'TI', 'PP', 'NIT'];

export default function RegisterScreen() {
  const navigation = useNavigation<Nav>();
  const login = useAuthStore((s) => s.login);

  const [form, setForm] = useState({
    email: '', first_name: '', last_name: '',
    document_type: 'CC' as DocType, document_number: '',
    phone: '', password: '',
  });

  const set = (key: string, value: string) => setForm((prev) => ({ ...prev, [key]: value }));

  const mutation = useMutation({
    mutationFn: async () => {
      const tokens = await registerUser({ ...form, accept_terms: true, accept_data_policy: true });
      setAuthToken(tokens.access_token);
      const user = await getMe();
      return { tokens, user };
    },
    onSuccess: ({ tokens, user }) => login(tokens, user),
    onError: (e: Error) => Alert.alert('Error', e.message || 'No se pudo registrar'),
  });

  return (
    <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
      <ScrollView style={styles.container} contentContainerStyle={styles.content}>
        <Text style={styles.title}>Crear cuenta</Text>
        <Text style={styles.subtitle}>Completa tus datos</Text>

        {[
          { label: 'Nombre', key: 'first_name', placeholder: 'Juan' },
          { label: 'Apellido', key: 'last_name', placeholder: 'Pérez' },
          { label: 'Correo electrónico', key: 'email', placeholder: 'correo@ejemplo.com', keyboard: 'email-address' as const },
          { label: 'Número de documento', key: 'document_number', placeholder: '1234567890', keyboard: 'numeric' as const },
          { label: 'Teléfono', key: 'phone', placeholder: '3001234567', keyboard: 'phone-pad' as const },
        ].map(({ label, key, placeholder, keyboard }) => (
          <View key={key}>
            <Text style={styles.label}>{label}</Text>
            <TextInput
              style={styles.input}
              value={(form as any)[key]}
              onChangeText={(v) => set(key, v)}
              placeholder={placeholder}
              placeholderTextColor={colors.textMuted}
              keyboardType={keyboard}
              autoCapitalize="none"
            />
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

        <Text style={styles.label}>Contraseña</Text>
        <TextInput
          style={styles.input} value={form.password}
          onChangeText={(v) => set('password', v)}
          secureTextEntry placeholder="Mín. 8 caracteres"
          placeholderTextColor={colors.textMuted}
        />

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
            ¿Ya tienes cuenta? <Text style={styles.linkBold}>Inicia sesión</Text>
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