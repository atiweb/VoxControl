import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:voxcontrol/providers/connection_provider.dart';
import 'package:voxcontrol/theme/app_theme.dart';

class StatusBar extends StatelessWidget {
  const StatusBar({super.key});

  @override
  Widget build(BuildContext context) {
    final conn = context.watch<ConnectionProvider>();

    String statusText;
    Color statusColor;
    IconData statusIcon;

    switch (conn.state) {
      case VoxConnectionState.connected:
        statusText = 'Connected';
        statusColor = AppTheme.success;
        statusIcon = Icons.check_circle;
        break;
      case VoxConnectionState.connecting:
        statusText = 'Connecting...';
        statusColor = AppTheme.warning;
        statusIcon = Icons.sync;
        break;
      case VoxConnectionState.error:
        statusText = conn.errorMessage ?? 'Connection error';
        statusColor = AppTheme.error;
        statusIcon = Icons.error_outline;
        break;
      case VoxConnectionState.disconnected:
        statusText = 'Disconnected';
        statusColor = AppTheme.textSecondary;
        statusIcon = Icons.link_off;
        break;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      color: statusColor.withValues(alpha: 0.08),
      child: Row(
        children: [
          Icon(statusIcon, size: 16, color: statusColor),
          const SizedBox(width: 8),
          Text(
            statusText,
            style: TextStyle(color: statusColor, fontSize: 13),
          ),
          const Spacer(),
          if (conn.isProcessing)
            SizedBox(
              width: 14,
              height: 14,
              child: CircularProgressIndicator(
                strokeWidth: 2,
                color: Theme.of(context).colorScheme.primary,
              ),
            ),
        ],
      ),
    );
  }
}
