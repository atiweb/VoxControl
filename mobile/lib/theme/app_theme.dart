import 'package:flutter/material.dart';

class AppTheme {
  static const _primaryColor = Color(0xFF6C63FF);
  static const _accentColor = Color(0xFF00D9FF);
  static const _bgDark = Color(0xFF0D1117);
  static const _surfaceDark = Color(0xFF161B22);
  static const _cardDark = Color(0xFF21262D);
  static const _textPrimary = Color(0xFFE6EDF3);
  static const _textSecondary = Color(0xFF8B949E);
  static const _success = Color(0xFF3FB950);
  static const _error = Color(0xFFF85149);
  static const _warning = Color(0xFFD29922);

  // Public accessors for widgets
  static const Color primary = _primaryColor;
  static const Color accent = _accentColor;
  static const Color success = _success;
  static const Color error = _error;
  static const Color warning = _warning;
  static const Color textSecondary = _textSecondary;

  static ThemeData get darkTheme => ThemeData(
        brightness: Brightness.dark,
        scaffoldBackgroundColor: _bgDark,
        primaryColor: _primaryColor,
        colorScheme: const ColorScheme.dark(
          primary: _primaryColor,
          secondary: _accentColor,
          surface: _surfaceDark,
          error: _error,
          onPrimary: Colors.white,
          onSecondary: Colors.white,
          onSurface: _textPrimary,
          onError: Colors.white,
        ),
        appBarTheme: const AppBarTheme(
          backgroundColor: _surfaceDark,
          elevation: 0,
          centerTitle: true,
          titleTextStyle: TextStyle(
            color: _textPrimary,
            fontSize: 20,
            fontWeight: FontWeight.w600,
          ),
          iconTheme: IconThemeData(color: _textPrimary),
        ),
        cardTheme: CardTheme(
          color: _cardDark,
          elevation: 0,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
            side: BorderSide(color: Colors.white.withValues(alpha: 0.06)),
          ),
        ),
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            backgroundColor: _primaryColor,
            foregroundColor: Colors.white,
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(10),
            ),
            textStyle: const TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w600,
            ),
          ),
        ),
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: _cardDark,
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(10),
            borderSide: BorderSide(color: Colors.white.withValues(alpha: 0.1)),
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(10),
            borderSide: BorderSide(color: Colors.white.withValues(alpha: 0.1)),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(10),
            borderSide: const BorderSide(color: _primaryColor, width: 2),
          ),
          hintStyle: const TextStyle(color: _textSecondary),
          labelStyle: const TextStyle(color: _textSecondary),
          contentPadding:
              const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        ),
        textTheme: const TextTheme(
          headlineLarge: TextStyle(
            color: _textPrimary,
            fontSize: 28,
            fontWeight: FontWeight.bold,
          ),
          headlineMedium: TextStyle(
            color: _textPrimary,
            fontSize: 22,
            fontWeight: FontWeight.w600,
          ),
          titleLarge: TextStyle(
            color: _textPrimary,
            fontSize: 18,
            fontWeight: FontWeight.w600,
          ),
          bodyLarge: TextStyle(color: _textPrimary, fontSize: 16),
          bodyMedium: TextStyle(color: _textSecondary, fontSize: 14),
          labelLarge: TextStyle(
            color: _textPrimary,
            fontSize: 14,
            fontWeight: FontWeight.w500,
          ),
        ),
        dividerTheme: DividerThemeData(
          color: Colors.white.withValues(alpha: 0.06),
          thickness: 1,
        ),
        snackBarTheme: SnackBarThemeData(
          backgroundColor: _cardDark,
          contentTextStyle: const TextStyle(color: _textPrimary),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8),
          ),
          behavior: SnackBarBehavior.floating,
        ),
      );

  // Semantic colors
  static const Color success = _success;
  static const Color error = _error;
  static const Color warning = _warning;
  static const Color accent = _accentColor;
  static const Color primary = _primaryColor;
  static const Color textSecondary = _textSecondary;
}
