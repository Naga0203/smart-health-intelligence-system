import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Alert, useTheme, alpha } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';

// Validation schema
const loginSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
});

type LoginFormData = z.infer<typeof loginSchema>;

interface LoginFormProps {
  onSubmit: (email: string, password: string) => Promise<void>;
  error: string | null;
  loading: boolean;
}

export const LoginForm: React.FC<LoginFormProps> = ({ onSubmit, error, loading }) => {
  const [emailFocused, setEmailFocused] = useState(false);
  const [passwordFocused, setPasswordFocused] = useState(false);
  const theme = useTheme();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  const { ref: emailRef, ...emailRest } = register('email');
  const { ref: passwordRef, ...passwordRest } = register('password');

  const handleFormSubmit = async (data: LoginFormData) => {
    await onSubmit(data.email, data.password);
  };

  const inputStyle = (focused: boolean): React.CSSProperties => ({
    width: '100%',
    background: alpha(theme.palette.background.paper, 0.4),
    border: `1px solid ${focused ? theme.palette.primary.main : alpha(theme.palette.divider, 0.2)}`,
    padding: '16px 22px',
    borderRadius: '16px',
    marginTop: '16px',
    boxShadow: focused ? `0 0 0 3px ${alpha(theme.palette.primary.main, 0.2)}` : 'none',
    outline: 'none',
    fontSize: '15px',
    color: theme.palette.text.primary,
    boxSizing: 'border-box',
    transition: 'all 0.2s',
    fontFamily: theme.typography.fontFamily,
  });

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} noValidate style={{ marginTop: '24px' }}>
      {error && (
        <Alert severity="error" sx={{ mb: 2, borderRadius: '12px' }}>
          {error}
        </Alert>
      )}

      <input
        {...emailRest}
        ref={(e) => {
          emailRef(e);
        }}
        type="email"
        placeholder="E-mail"
        disabled={loading}
        style={inputStyle(emailFocused)}
        onFocus={() => setEmailFocused(true)}
        onBlur={() => setEmailFocused(false)}
        autoComplete="email"
      />
      {errors.email && (
        <span style={{ fontSize: '12px', color: theme.palette.error.main, marginLeft: '10px', display: 'block', marginTop: '4px' }}>
          {errors.email.message}
        </span>
      )}

      <input
        {...passwordRest}
        ref={(e) => {
          passwordRef(e);
        }}
        type="password"
        placeholder="Password"
        disabled={loading}
        style={inputStyle(passwordFocused)}
        onFocus={() => setPasswordFocused(true)}
        onBlur={() => setPasswordFocused(false)}
        autoComplete="current-password"
      />
      {errors.password && (
        <span style={{ fontSize: '12px', color: theme.palette.error.main, marginLeft: '10px', display: 'block', marginTop: '4px' }}>
          {errors.password.message}
        </span>
      )}

      <span style={{ display: 'block', marginTop: '12px', marginLeft: '4px' }}>
        <RouterLink
          to="/forgot-password"
          style={{ fontSize: '13px', color: theme.palette.primary.main, textDecoration: 'none', fontWeight: 500 }}
        >
          Forgot Password?
        </RouterLink>
      </span>

      <button
        type="submit"
        disabled={loading}
        style={{
          display: 'block',
          width: '100%',
          fontWeight: 600,
          background: theme.palette.primary.main,
          color: 'white',
          padding: '16px 0',
          margin: '24px auto 0',
          borderRadius: '16px',
          boxShadow: `0 8px 24px ${alpha(theme.palette.primary.main, 0.4)}`,
          border: 'none',
          cursor: loading ? 'not-allowed' : 'pointer',
          fontSize: '16px',
          letterSpacing: '0.3px',
          transition: 'all 0.2s ease-in-out',
          opacity: loading ? 0.8 : 1,
          fontFamily: theme.typography.fontFamily,
        }}
        onMouseEnter={(e) => {
          if (!loading) {
            (e.currentTarget as HTMLButtonElement).style.transform = 'translateY(-2px)';
            (e.currentTarget as HTMLButtonElement).style.boxShadow = `0 12px 28px ${alpha(theme.palette.primary.main, 0.6)}`;
            (e.currentTarget as HTMLButtonElement).style.background = theme.palette.primary.dark;
          }
        }}
        onMouseLeave={(e) => {
          (e.currentTarget as HTMLButtonElement).style.transform = 'translateY(0)';
          (e.currentTarget as HTMLButtonElement).style.boxShadow = `0 8px 24px ${alpha(theme.palette.primary.main, 0.4)}`;
          (e.currentTarget as HTMLButtonElement).style.background = theme.palette.primary.main;
        }}
        onMouseDown={(e) => {
          if (!loading) {
            (e.currentTarget as HTMLButtonElement).style.transform = 'translateY(1px)';
          }
        }}
        onMouseUp={(e) => {
          if (!loading) {
            (e.currentTarget as HTMLButtonElement).style.transform = 'translateY(-2px)';
          }
        }}
      >
        {loading ? 'Signing in...' : 'Sign In'}
      </button>
    </form>
  );
};
