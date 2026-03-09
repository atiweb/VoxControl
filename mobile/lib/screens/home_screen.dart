import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:voxcontrol/providers/auth_provider.dart';
import 'package:voxcontrol/providers/connection_provider.dart';
import 'package:voxcontrol/screens/connect_screen.dart';
import 'package:voxcontrol/theme/app_theme.dart';
import 'package:voxcontrol/widgets/command_input.dart';
import 'package:voxcontrol/widgets/history_list.dart';
import 'package:voxcontrol/widgets/mic_button.dart';
import 'package:voxcontrol/widgets/quick_actions.dart';
import 'package:voxcontrol/widgets/status_bar.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  @override
  void initState() {
    super.initState();
    // Auto-connect if not already connected
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final conn = context.read<ConnectionProvider>();
      if (!conn.isConnected) conn.connect();
    });
  }

  void _logout() async {
    final auth = context.read<AuthProvider>();
    final conn = context.read<ConnectionProvider>();
    conn.disconnect();
    await auth.logout();
    if (!mounted) return;
    Navigator.of(context).pushAndRemoveUntil(
      MaterialPageRoute(builder: (_) => const ConnectScreen()),
      (route) => false,
    );
  }

  @override
  Widget build(BuildContext context) {
    final conn = context.watch<ConnectionProvider>();
    final auth = context.watch<AuthProvider>();

    return Scaffold(
      appBar: AppBar(
        title: const Text('VoxControl'),
        leading: Padding(
          padding: const EdgeInsets.all(8),
          child: Container(
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              gradient: LinearGradient(
                colors: [
                  Theme.of(context).colorScheme.primary,
                  Theme.of(context).colorScheme.secondary,
                ],
              ),
            ),
            child: const Icon(Icons.mic, size: 20, color: Colors.white),
          ),
        ),
        actions: [
          // Connection indicator
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 8),
            child: Icon(
              Icons.circle,
              size: 10,
              color: conn.isConnected ? AppTheme.success : AppTheme.error,
            ),
          ),
          PopupMenuButton<String>(
            icon: const Icon(Icons.more_vert),
            onSelected: (value) {
              if (value == 'logout') _logout();
              if (value == 'clear') conn.clearHistory();
              if (value == 'reconnect') conn.connect();
            },
            itemBuilder: (_) => [
              if (auth.username != null)
                PopupMenuItem(
                  enabled: false,
                  child: Text(
                    'User: ${auth.username}',
                    style: const TextStyle(color: AppTheme.textSecondary),
                  ),
                ),
              const PopupMenuItem(
                value: 'reconnect',
                child: ListTile(
                  leading: Icon(Icons.refresh),
                  title: Text('Reconnect'),
                  dense: true,
                  contentPadding: EdgeInsets.zero,
                ),
              ),
              const PopupMenuItem(
                value: 'clear',
                child: ListTile(
                  leading: Icon(Icons.delete_sweep),
                  title: Text('Clear History'),
                  dense: true,
                  contentPadding: EdgeInsets.zero,
                ),
              ),
              const PopupMenuDivider(),
              const PopupMenuItem(
                value: 'logout',
                child: ListTile(
                  leading: Icon(Icons.logout, color: AppTheme.error),
                  title: Text('Disconnect',
                      style: TextStyle(color: AppTheme.error)),
                  dense: true,
                  contentPadding: EdgeInsets.zero,
                ),
              ),
            ],
          ),
        ],
      ),
      body: Column(
        children: [
          // Status bar
          const StatusBar(),

          // Quick actions
          const QuickActions(),

          const Divider(height: 1),

          // Command history
          const Expanded(child: HistoryList()),

          // Input area
          const CommandInput(),
        ],
      ),
      // Floating mic button
      floatingActionButton: const MicButton(),
      floatingActionButtonLocation: FloatingActionButtonLocation.centerFloat,
    );
  }
}
