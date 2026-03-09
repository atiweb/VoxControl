import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:voxcontrol/providers/auth_provider.dart';
import 'package:voxcontrol/screens/login_screen.dart';
import 'package:voxcontrol/screens/home_screen.dart';
import 'package:voxcontrol/theme/app_theme.dart';

class ConnectScreen extends StatefulWidget {
  const ConnectScreen({super.key});

  @override
  State<ConnectScreen> createState() => _ConnectScreenState();
}

class _ConnectScreenState extends State<ConnectScreen> {
  final _urlController = TextEditingController();
  final _formKey = GlobalKey<FormState>();
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    final auth = context.read<AuthProvider>();
    if (auth.serverUrl != null) {
      _urlController.text = auth.serverUrl!;
    }
  }

  @override
  void dispose() {
    _urlController.dispose();
    super.dispose();
  }

  Future<void> _connect() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isLoading = true);

    final auth = context.read<AuthProvider>();
    await auth.setServer(_urlController.text.trim());

    setState(() => _isLoading = false);

    if (!mounted) return;

    if (auth.isAuthenticated) {
      // No auth required — go straight to home
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(builder: (_) => const HomeScreen()),
      );
    } else if (auth.state == AuthState.unauthenticated) {
      Navigator.of(context).push(
        MaterialPageRoute(builder: (_) => const LoginScreen()),
      );
    } else if (auth.state == AuthState.error) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(auth.errorMessage ?? 'Connection failed'),
          backgroundColor: AppTheme.error,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Form(
            key: _formKey,
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // Logo
                Container(
                  width: 80,
                  height: 80,
                  alignment: Alignment.center,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    gradient: LinearGradient(
                      colors: [
                        Theme.of(context).colorScheme.primary,
                        Theme.of(context).colorScheme.secondary,
                      ],
                    ),
                  ),
                  child: const Icon(Icons.mic, size: 40, color: Colors.white),
                ),
                const SizedBox(height: 24),
                Text(
                  'Connect to VoxControl',
                  textAlign: TextAlign.center,
                  style: Theme.of(context).textTheme.headlineMedium,
                ),
                const SizedBox(height: 8),
                Text(
                  'Enter your PC\'s IP address and port',
                  textAlign: TextAlign.center,
                  style: Theme.of(context).textTheme.bodyMedium,
                ),
                const SizedBox(height: 40),

                // URL field
                TextFormField(
                  controller: _urlController,
                  keyboardType: TextInputType.url,
                  decoration: const InputDecoration(
                    labelText: 'Server URL',
                    hintText: 'http://192.168.1.100:8765',
                    prefixIcon: Icon(Icons.dns_outlined),
                  ),
                  validator: (val) {
                    if (val == null || val.trim().isEmpty) {
                      return 'Please enter the server URL';
                    }
                    final uri = Uri.tryParse(val.trim());
                    if (uri == null || !uri.hasScheme) {
                      return 'Enter a valid URL (e.g. http://192.168.1.100:8765)';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 24),

                // Connect button
                SizedBox(
                  height: 50,
                  child: ElevatedButton(
                    onPressed: _isLoading ? null : _connect,
                    child: _isLoading
                        ? const SizedBox(
                            width: 20,
                            height: 20,
                            child:
                                CircularProgressIndicator(strokeWidth: 2),
                          )
                        : const Text('Connect'),
                  ),
                ),
                const SizedBox(height: 16),

                // Help text
                Text(
                  'Make sure VoxControl is running on your PC\n'
                  'and your phone is on the same Wi-Fi network.',
                  textAlign: TextAlign.center,
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        fontSize: 12,
                      ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
