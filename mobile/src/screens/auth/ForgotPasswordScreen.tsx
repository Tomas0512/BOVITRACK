import { useState } from 'react';
import {
  View, Text, TextInput, TouchableOpacity, StyleSheet,
  ActivityIndicator, KeyboardAvoidingView, Platform, ScrollView,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { useMutation } from '@tanstack/react-query';
import { forgotPassword } from '../../services/auth';
import { AuthStackParamList } from '../../navigation/AuthNavigator';
import { colors } from '../../theme/colors';

type Nav = NativeStackNavigationProp<AuthStackParamList, 'ForgotPassword'>;

export default function ForgotPasswordScreen() {
  const navigation = useNavigation<Nav>();
  const [email, setEmail] = useState('');
  const [sent, setSent] = useState(false);

  const mutation = useMutation({
    mutationFn: () => forgotPassword(email),
    onSettled: () => setSent(true), // siempre muestra éxito
  });

  if (sent) {
    return (
      <View style={styles.container}>
        <View style={styles.successBox}>
          <Text style={styles.successIcon}>✅</Text>
          <Text style={styles.successTitle}>Revisa tu correo</Text>
          <Text style={styles.successText}>
            Si existe una cuenta con ese correo, recibirás un enlace para restablecer tu contraseña.
          </Text>
        </View>
        <TouchableOpacity style={styles.btnPrimary} onPress={() => navigation.navigate('Login')}>
          <Text style={styles.btnPrimaryText}>Volver al login</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
      <ScrollView style={styles.container} contentContainerStyle={styles.content}>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Text style={styles.back}>← Volver</Text>
        </TouchableOpacity>

        <Text style={styles.title}>Olvidé mi contraseña</Text>
        <Text style={styles.subtitle}>Ingresa tu correo y te enviaremos un enlace de recuperación.</Text>

        <Text style={styles.label}>Correo electrónico</Text>
        <TextInput
          style={styles.input} value={email} onChangeText={setEmail}
          keyboardType="email-address" autoCapitalize="none"
          placeholder="correo@ejemplo.com" placeholderTextColor={colors.textMuted}
        />

        <TouchableOpacity
          style={[styles.btnPrimary, mutation.isPending && styles.btnDisabled]}
          onPress={() => mutation.mutate()}
          disabled={mutation.isPending}
        >
          {mutation.isPending
            ? <ActivityIndicator color={colors.textOnPrimary} />
            : <Text style={styles.btnPrimaryText}>Enviar enlace</Text>}
        </TouchableOpacity>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  content: { padding: 24, paddingTop: 64 },
  back: { color: colors.primary, fontSize: 15, marginBottom: 24 },
  title: { fontSize: 28, fontWeight: 'bold', color: colors.primaryDark, marginBottom: 8 },
  subtitle: { fontSize: 15, color: colors.textSecondary, marginBottom: 32 },
  label: { fontSize: 14, fontWeight: '600', color: colors.textPrimary, marginBottom: 6 },
  input: {
    borderWidth: 1, borderColor: colors.border, borderRadius: 10,
    padding: 14, fontSize: 15, color: colors.textPrimary,
    backgroundColor: colors.surface, marginBottom: 16,
  },
  btnPrimary: {
    backgroundColor: colors.primary, borderRadius: 10,
    padding: 16, alignItems: 'center',
  },
  btnDisabled: { opacity: 0.6 },
  btnPrimaryText: { color: colors.textOnPrimary, fontWeight: '700', fontSize: 16 },
  successBox: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 32 },
  successIcon: { fontSize: 56, marginBottom: 16 },
  successTitle: { fontSize: 22, fontWeight: 'bold', color: colors.primaryDark, marginBottom: 12 },
  successText: { fontSize: 15, color: colors.textSecondary, textAlign: 'center' },
});