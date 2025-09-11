/**
 * 📝 Typography Design Tokens
 * Comprehensive typography system for Nexus Platform
 */

export const typography = {
  // Font Families
  fontFamily: {
    sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
    mono: ['JetBrains Mono', 'Fira Code', 'Monaco', 'Consolas', 'monospace'],
    display: ['Inter', 'system-ui', 'sans-serif'],
  },

  // Font Sizes
  fontSize: {
    xs: '0.75rem',    // 12px
    sm: '0.875rem',   // 14px
    base: '1rem',     // 16px
    lg: '1.125rem',   // 18px
    xl: '1.25rem',    // 20px
    '2xl': '1.5rem',  // 24px
    '3xl': '1.875rem', // 30px
    '4xl': '2.25rem', // 36px
    '5xl': '3rem',    // 48px
    '6xl': '3.75rem', // 60px
    '7xl': '4.5rem',  // 72px
    '8xl': '6rem',    // 96px
    '9xl': '8rem',    // 128px
  },

  // Font Weights
  fontWeight: {
    thin: '100',
    extralight: '200',
    light: '300',
    normal: '400',
    medium: '500',
    semibold: '600',
    bold: '700',
    extrabold: '800',
    black: '900',
  },

  // Line Heights
  lineHeight: {
    none: '1',
    tight: '1.25',
    snug: '1.375',
    normal: '1.5',
    relaxed: '1.625',
    loose: '2',
  },

  // Letter Spacing
  letterSpacing: {
    tighter: '-0.05em',
    tight: '-0.025em',
    normal: '0em',
    wide: '0.025em',
    wider: '0.05em',
    widest: '0.1em',
  },

  // Text Styles
  textStyles: {
    // Display Styles
    'display-2xl': {
      fontSize: '4.5rem',
      lineHeight: '1',
      fontWeight: '800',
      letterSpacing: '-0.025em',
    },
    'display-xl': {
      fontSize: '3.75rem',
      lineHeight: '1',
      fontWeight: '800',
      letterSpacing: '-0.025em',
    },
    'display-lg': {
      fontSize: '3rem',
      lineHeight: '1.2',
      fontWeight: '800',
      letterSpacing: '-0.025em',
    },
    'display-md': {
      fontSize: '2.25rem',
      lineHeight: '1.2',
      fontWeight: '800',
      letterSpacing: '-0.025em',
    },
    'display-sm': {
      fontSize: '1.875rem',
      lineHeight: '1.3',
      fontWeight: '600',
      letterSpacing: '-0.025em',
    },
    'display-xs': {
      fontSize: '1.5rem',
      lineHeight: '1.4',
      fontWeight: '600',
      letterSpacing: '-0.025em',
    },

    // Heading Styles
    'h1': {
      fontSize: '2.25rem',
      lineHeight: '1.2',
      fontWeight: '700',
      letterSpacing: '-0.025em',
    },
    'h2': {
      fontSize: '1.875rem',
      lineHeight: '1.3',
      fontWeight: '700',
      letterSpacing: '-0.025em',
    },
    'h3': {
      fontSize: '1.5rem',
      lineHeight: '1.4',
      fontWeight: '600',
      letterSpacing: '-0.025em',
    },
    'h4': {
      fontSize: '1.25rem',
      lineHeight: '1.4',
      fontWeight: '600',
      letterSpacing: '-0.025em',
    },
    'h5': {
      fontSize: '1.125rem',
      lineHeight: '1.4',
      fontWeight: '600',
      letterSpacing: '-0.025em',
    },
    'h6': {
      fontSize: '1rem',
      lineHeight: '1.4',
      fontWeight: '600',
      letterSpacing: '-0.025em',
    },

    // Body Styles
    'body-xl': {
      fontSize: '1.25rem',
      lineHeight: '1.6',
      fontWeight: '400',
    },
    'body-lg': {
      fontSize: '1.125rem',
      lineHeight: '1.6',
      fontWeight: '400',
    },
    'body-md': {
      fontSize: '1rem',
      lineHeight: '1.6',
      fontWeight: '400',
    },
    'body-sm': {
      fontSize: '0.875rem',
      lineHeight: '1.5',
      fontWeight: '400',
    },
    'body-xs': {
      fontSize: '0.75rem',
      lineHeight: '1.5',
      fontWeight: '400',
    },

    // Label Styles
    'label-lg': {
      fontSize: '1.125rem',
      lineHeight: '1.4',
      fontWeight: '500',
    },
    'label-md': {
      fontSize: '1rem',
      lineHeight: '1.4',
      fontWeight: '500',
    },
    'label-sm': {
      fontSize: '0.875rem',
      lineHeight: '1.4',
      fontWeight: '500',
    },
    'label-xs': {
      fontSize: '0.75rem',
      lineHeight: '1.4',
      fontWeight: '500',
    },

    // Caption Styles
    'caption-lg': {
      fontSize: '0.875rem',
      lineHeight: '1.4',
      fontWeight: '400',
    },
    'caption-md': {
      fontSize: '0.75rem',
      lineHeight: '1.4',
      fontWeight: '400',
    },
    'caption-sm': {
      fontSize: '0.625rem',
      lineHeight: '1.4',
      fontWeight: '400',
    },

    // Code Styles
    'code-lg': {
      fontFamily: 'JetBrains Mono, monospace',
      fontSize: '1rem',
      lineHeight: '1.6',
      fontWeight: '400',
    },
    'code-md': {
      fontFamily: 'JetBrains Mono, monospace',
      fontSize: '0.875rem',
      lineHeight: '1.5',
      fontWeight: '400',
    },
    'code-sm': {
      fontFamily: 'JetBrains Mono, monospace',
      fontSize: '0.75rem',
      lineHeight: '1.5',
      fontWeight: '400',
    },
  },

  // Responsive Typography
  responsive: {
    // Mobile-first approach
    mobile: {
      'display-2xl': '2.5rem',
      'display-xl': '2.25rem',
      'display-lg': '2rem',
      'display-md': '1.875rem',
      'display-sm': '1.5rem',
      'display-xs': '1.25rem',
      'h1': '1.875rem',
      'h2': '1.5rem',
      'h3': '1.25rem',
      'h4': '1.125rem',
      'h5': '1rem',
      'h6': '0.875rem',
    },
    tablet: {
      'display-2xl': '3.5rem',
      'display-xl': '3rem',
      'display-lg': '2.5rem',
      'display-md': '2rem',
      'display-sm': '1.75rem',
      'display-xs': '1.5rem',
      'h1': '2rem',
      'h2': '1.75rem',
      'h3': '1.5rem',
      'h4': '1.25rem',
      'h5': '1.125rem',
      'h6': '1rem',
    },
    desktop: {
      'display-2xl': '4.5rem',
      'display-xl': '3.75rem',
      'display-lg': '3rem',
      'display-md': '2.25rem',
      'display-sm': '1.875rem',
      'display-xs': '1.5rem',
      'h1': '2.25rem',
      'h2': '1.875rem',
      'h3': '1.5rem',
      'h4': '1.25rem',
      'h5': '1.125rem',
      'h6': '1rem',
    },
  },
} as const;

// Typography utility functions
export const getFontSize = (size: keyof typeof typography.fontSize) => typography.fontSize[size];
export const getFontWeight = (weight: keyof typeof typography.fontWeight) => typography.fontWeight[weight];
export const getLineHeight = (height: keyof typeof typography.lineHeight) => typography.lineHeight[height];
export const getLetterSpacing = (spacing: keyof typeof typography.letterSpacing) => typography.letterSpacing[spacing];

// Text style utilities
export const getTextStyle = (style: keyof typeof typography.textStyles) => typography.textStyles[style];

// Responsive typography utilities
export const getResponsiveFontSize = (
  style: keyof typeof typography.textStyles,
  breakpoint: 'mobile' | 'tablet' | 'desktop' = 'desktop'
) => {
  const responsiveSize = typography.responsive[breakpoint][style as keyof typeof typography.responsive.mobile];
  return responsiveSize || typography.textStyles[style].fontSize;
};

// Typography scale for consistent sizing
export const typographyScale = {
  // Perfect Fourth scale (1.333)
  scale: 1.333,
  baseSize: 16, // 16px base
  
  // Generate scale
  generateScale: (steps: number) => {
    const scale = [];
    for (let i = 0; i < steps; i++) {
      scale.push(typographyScale.baseSize * Math.pow(typographyScale.scale, i - 2));
    }
    return scale;
  },
};

// Accessibility helpers
export const getReadableFontSize = (baseSize: number, contrast: 'normal' | 'high' = 'normal') => {
  const multiplier = contrast === 'high' ? 1.2 : 1;
  return Math.max(baseSize * multiplier, 14); // Minimum 14px for accessibility
};

export const getOptimalLineHeight = (fontSize: number) => {
  // Optimal line height is typically 1.4-1.6 times the font size
  return Math.round(fontSize * 1.5);
};

export type TypographySize = keyof typeof typography.fontSize;
export type TypographyWeight = keyof typeof typography.fontWeight;
export type TypographyStyle = keyof typeof typography.textStyles;
export type ResponsiveBreakpoint = keyof typeof typography.responsive;
