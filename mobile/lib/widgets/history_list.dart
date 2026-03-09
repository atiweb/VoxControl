import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:voxcontrol/providers/connection_provider.dart';
import 'package:voxcontrol/theme/app_theme.dart';

class HistoryList extends StatelessWidget {
  const HistoryList({super.key});

  @override
  Widget build(BuildContext context) {
    final conn = context.watch<ConnectionProvider>();
    final history = conn.history;

    if (history.isEmpty) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              Icons.mic_none,
              size: 64,
              color: AppTheme.textSecondary.withValues(alpha: 0.3),
            ),
            const SizedBox(height: 16),
            Text(
              'Tap the mic or type a command',
              style: Theme.of(context).textTheme.bodyMedium,
            ),
            const SizedBox(height: 4),
            Text(
              'e.g. "open chrome", "take screenshot"',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    fontSize: 12,
                    color: AppTheme.textSecondary.withValues(alpha: 0.5),
                  ),
            ),
          ],
        ),
      );
    }

    return ListView.builder(
      reverse: true,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      itemCount: history.length,
      itemBuilder: (context, index) {
        // Reversed — show newest at bottom
        final item = history[history.length - 1 - index];
        final isCommand = item['type'] == 'command';

        return Align(
          alignment:
              isCommand ? Alignment.centerRight : Alignment.centerLeft,
          child: Container(
            margin: const EdgeInsets.symmetric(vertical: 4),
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
            constraints: BoxConstraints(
              maxWidth: MediaQuery.of(context).size.width * 0.75,
            ),
            decoration: BoxDecoration(
              color: isCommand
                  ? Theme.of(context).colorScheme.primary.withValues(alpha: 0.15)
                  : Theme.of(context).cardTheme.color,
              borderRadius: BorderRadius.circular(16).copyWith(
                bottomRight: isCommand
                    ? const Radius.circular(4)
                    : const Radius.circular(16),
                bottomLeft: isCommand
                    ? const Radius.circular(16)
                    : const Radius.circular(4),
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (!isCommand)
                  Padding(
                    padding: const EdgeInsets.only(bottom: 2),
                    child: Text(
                      'VoxControl',
                      style: TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.w600,
                        color: Theme.of(context).colorScheme.secondary,
                      ),
                    ),
                  ),
                Text(
                  item['text'] ?? '',
                  style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                        fontSize: 14,
                      ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}
