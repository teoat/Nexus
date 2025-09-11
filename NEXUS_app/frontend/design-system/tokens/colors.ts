 /**
 * 🎨 Color Design Tokens
 * Comprehensive color system for Nexus Platform
 */

export const colors = {
    // Primary Colors - Modern Blue Gradient
    primary: {
      50: '#EFF6FF',
      100: '#DBEAFE',
      200: '#BFDBFE',
      300: '#93C5FD',
      400: '#60A5FA',
      500: '#3B82F6', // Main primary
      600: '#2563EB',
      700: '#1D4ED8',
      800: '#1E40AF',
      900: '#1E3A8A',
      950: '#172554',
    },
  
    // Secondary Colors - Purple Accent
    secondary: {
      50: '#FAF5FF',
      100: '#F3E8FF',
      200: '#E9D5FF',
      300: '#D8B4FE',
      400: '#C084FC',
      500: '#A855F7',
      600: '#9333EA',
      700: '#7C3AED', // Main secondary
      800: '#6B21A8',
      900: '#581C87',
      950: '#3B0764',
    },
  
    // Success Colors - Green
    success: {
      50: '#ECFDF5',
      100: '#D1FAE5',
      200: '#A7F3D0',
      300: '#6EE7B7',
      400: '#34D399',
      500: '#10B981', // Main success
      600: '#059669',
      700: '#047857',
      800: '#065F46',
      900: '#064E3B',
      950: '#022C22',
    },
  
    // Warning Colors - Amber
    warning: {
      50: '#FFFBEB',
      100: '#FEF3C7',
      200: '#FDE68A',
      300: '#FCD34D',
      400: '#FBBF24',
      500: '#F59E0B', // Main warning
      600: '#D97706',
      700: '#B45309',
      800: '#92400E',
      900: '#78350F',
      950: '#451A03',
    },
  
    // Error Colors - Red
    error: {
      50: '#FEF2F2',
      100: '#FEE2E2',
      200: '#FECACA',
      300: '#FCA5A5',
      400: '#F87171',
      500: '#EF4444', // Main error
      600: '#DC2626',
      700: '#B91C1C',
      800: '#991B1B',
      900: '#7F1D1D',
      950: '#450A0A',
    },
  
    // Neutral Colors - Gray Scale
    neutral: {
      50: '#F9FAFB',
      100: '#F3F4F6',
      200: '#E5E7EB',
      300: '#D1D5DB',
      400: '#9CA3AF',
      500: '#6B7280',
      600: '#4B5563',
      700: '#374151',
      800: '#1F2937',
      900: '#111827', // Main dark
      950: '#030712',
    },
  
    // Semantic Colors
    semantic: {
      // Background Colors
      background: {
        primary: '#FFFFFF',
        secondary: '#F9FAFB',
        tertiary: '#F3F4F6',
        dark: '#111827',
        card: '#FFFFFF',
        overlay: 'rgba(0, 0, 0, 0.5)',
      },
  
      // Text Colors
      text: {
        primary: '#111827',
        secondary: '#6B7280',
        tertiary: '#9CA3AF',
        inverse: '#FFFFFF',
        disabled: '#D1D5DB',
        link: '#3B82F6',
        linkHover: '#2563EB',
      },
  
      // Border Colors
      border: {
        primary: '#E5E7EB',
        secondary: '#D1D5DB',
        focus: '#3B82F6',
        error: '#EF4444',
        success: '#10B981',
        warning: '#F59E0B',
      },
  
      // Status Colors
      status: {
        online: '#10B981',
        offline: '#6B7280',
        busy: '#F59E0B',
        away: '#EF4444',
        pending: '#F59E0B',
        completed: '#10B981',
        failed: '#EF4444',
        processing: '#3B82F6',
      },
    },
  
    // Data Visualization Colors
    chart: {
      primary: '#3B82F6',
      secondary: '#8B5CF6',
      success: '#10B981',
      warning: '#F59E0B',
      error: '#EF4444',
      info: '#06B6D4',
      purple: '#8B5CF6',
      pink: '#EC4899',
      indigo: '#6366F1',
      teal: '#14B8A6',
      orange: '#F97316',
      cyan: '#06B6D4',
      lime: '#84CC16',
      rose: '#F43F5E',
      violet: '#8B5CF6',
      emerald: '#10B981',
      sky: '#0EA5E9',
      amber: '#F59E0B',
      red: '#EF4444',
      blue: '#3B82F6',
      green: '#22C55E',
      yellow: '#EAB308',
    },
  
    // Gradient Colors
    gradients: {
      primary: 'linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%)',
      secondary: 'linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%)',
      success: 'linear-gradient(135deg, #10B981 0%, #059669 100%)',
      warning: 'linear-gradient(135deg, #F59E0B 0%, #D97706 100%)',
      error: 'linear-gradient(135deg, #EF4444 0%, #DC2626 100%)',
      neutral: 'linear-gradient(135deg, #6B7280 0%, #374151 100%)',
      rainbow: 'linear-gradient(135deg, #3B82F6 0%, #8B5CF6 25%, #EC4899 50%, #F59E0B 75%, #10B981 100%)',
    },
  
    // Dark Mode Colors
    dark: {
      background: {
        primary: '#111827',
        secondary: '#1F2937',
        tertiary: '#374151',
        card: '#1F2937',
        overlay: 'rgba(0, 0, 0, 0.8)',
      },
      text: {
        primary: '#F9FAFB',
        secondary: '#D1D5DB',
        tertiary: '#9CA3AF',
        inverse: '#111827',
        disabled: '#6B7280',
        link: '#60A5FA',
        linkHover: '#93C5FD',
      },
      border: {
        primary: '#374151',
        secondary: '#4B5563',
        focus: '#60A5FA',
        error: '#F87171',
        success: '#34D399',
        warning: '#FBBF24',
      },
    },
  } as const;
  
  // Color utility functions
  export const getColor = (path: string) => {
    const keys = path.split('.');
    let value: any = colors;
    
    for (const key of keys) {
      value = value?.[key];
      if (value === undefined) return undefined;
    }
    
    return value;
  };
  
  // Generate color variations
  export const generateColorVariations = (baseColor: string) => {
    return {
      light: `${baseColor}20`, // 20% opacity
      medium: `${baseColor}40`, // 40% opacity
      strong: `${baseColor}60`, // 60% opacity
      solid: baseColor,
    };
  };
  
  // Accessibility helpers
  export const getContrastRatio = (foreground: string, background: string): number => {
    // Simplified contrast ratio calculation
    // In a real implementation, you'd use a proper color contrast library
  };
  
  export const isAccessible = (foreground: string, background: string): boolean => {
    return getContrastRatio(foreground, background) >= 4.5;
  };
  
  // Theme configuration
  export const themes = {
    light: {
      background: colors.semantic.background.primary,
      text: colors.semantic.text.primary,
      border: colors.semantic.border.primary,
    },
    dark: {
      background: colors.dark.background.primary,
      text: colors.dark.text.primary,
      border: colors.dark.border.primary,
    },
  } as const;
  
  export type ColorTheme = keyof typeof themes;
  export type ColorPath = keyof typeof colors;