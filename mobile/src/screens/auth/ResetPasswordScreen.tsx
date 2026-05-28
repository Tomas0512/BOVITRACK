import { useState } from 'react';
import {
  View, Text, TextInput, TouchableOpacity, StyleSheet,
  ActivityIndicator, Alert, KeyboardAvoidingView, Platform, ScrollView,
} from 'react-native';
import { useNavigation, useRoute, RouteProp } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { useMutation } from '@tanstack/react-query';
import { resetPassword } from '../../services/auth';
import { AuthStackParamList } from '../../navigation/AuthNavigator';
import { colors } from '../../theme/colors';

type Nav = NativeStackNavigationProp<AuthStackParamList, 'ResetPassword'>;
type Route = RouteProp<AuthStackParamList, 'ResetPassword'>;

function validatePassword(pwd: string) {
  if (pwd.length < 8) return 'Mínimo 8 caracteres';
  if (!/[A-Z]/.test(pwd)) return 'Debe tener al menos una mayúscula';
  if (!/[a-z]/.test(pwd)) return 'Debe tener al menos una minúscula';
  if (!/[0-9]/.test(pwd)) return 'Debe tener al menos un número';
  return null;
}

export default function ResetPasswordScreen() {
  const navigation = useNavigation<Nav>();
  const route = useRoute<Route>();
  const { token } = route.params;

  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [done, setDone] = useState(false);

  const mutation = useMutation({
    mutationFn: () => {
      const error = validatePassword(password);
      if (error) return Promise.reject(new Error(error));
      if (password !== confirm) return Promise.reject(new Error('Las contraseñas no coinciden'));
      return resetPassword(token, password);
    },
    onSuccess: () => setDone(true),
    onError: (e: Error) => Alert.alert('Error', e.message),
  });

  if (done) {
    return (
      <View style={[styles.container, styles.center]}>
        <Text style={{ fontSize: 56, marginBottom: 16 }}>✅</Text>
        <Text style={styles.title}>Contraseña actualizada</Text>
        <Text style={styles.subtitle}>Ya puedes iniciar sesión con tu nueva contraseña.</Text>
        <TouchableOpacity style={styles.btnPrimary} onPress={() => navigation.navigate('Login')}>
          <Text style={styles.btnPrimaryText}>Ir al login</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
      <ScrollView style={styles.container} contentContainerStyle={styles.content}>
        <Text style={styles.title}>Nueva contraseña</Text>
        <Text style={styles.subtitle}>Mín. 8 caracteres, una mayúscula, una minúscula y un número.</Text>

        <Text style={styles.label}>Nueva contraseña</Text>
        <TextInput
          style={styles.input} value={password} onChangeText={setPassword}
          secureTextEntry placeholder="••••••••" placeholderTextColor={colors.textMuted}
        />

        <Text style={styles.label}>Confirmar contraseña</Text>
        <TextInput
          style={styles.input} value={confirm} onChangeText={setConfirm}
          secureTextEntry placeholder="••••••••" placeholderTextColor={colors.textMuted}
        />

        <TouchableOpacity
          style={[styles.btnPrimary, mutation.isPending && styles.btnDisabled]}
          onPress={() => mutation.mutate()}
          disabled={mutation.isPending}
        >
          {mutation.isPending
            ? <ActivityIndicator color={colors.textOnPrimary} />
            : <Text style={styles.btnPrimaryText}>Cambiar contraseña</Text>}
        </TouchableOpacity>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
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
  btnPrimary: {
    backgroundColor: colors.primary, borderRadius: 10,
    padding: 16, alignItems: 'center', marginTop: 8,
  },
  btnDisabled: { opacity: 0.6 },
  btnPrimaryText: { color: colors.textOnPrimary, fontWeight: '700', fontSize: 16 },
});