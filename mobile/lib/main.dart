import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:voxcontrol/providers/connection_provider.dart';
import 'package:voxcontrol/providers/auth_provider.dart';
import 'package:voxcontrol/screens/splash_screen.dart';
import 'package:voxcontrol/theme/app_theme.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const VoxControlApp());
}

class VoxControlApp extends StatelessWidget {
  const VoxControlApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthProvider()),
        ChangeNotifierProxyProvider<AuthProvider, ConnectionProvider>(
          create: (_) => ConnectionProvider(),
          update: (_, auth, conn) => conn!..updateAuth(auth),
        ),
      ],
      child: MaterialApp(
        title: 'VoxControl',
        debugShowCheckedModeBanner: false,
        theme: AppTheme.darkTheme,
        home: const SplashScreen(),
      ),
    );
  }
}
