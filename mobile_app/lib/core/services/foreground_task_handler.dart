import 'package:flutter_foreground_task/flutter_foreground_task.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

@pragma('vm:entry-point')
void startCallback() {
  FlutterForegroundTask.setTaskHandler(SyncTaskHandler());
}

@pragma('vm:entry-point')
class SyncTaskHandler extends TaskHandler {
  int _eventCount = 0;

  @override
  @pragma('vm:entry-point')
  Future<void> onStart(DateTime timestamp, TaskStarter starter) async {
    // Immediate refresh on startup
    _updateNotificationAsync();
  }

  @override
  @pragma('vm:entry-point')
  void onRepeatEvent(DateTime timestamp) {
    _eventCount++;
    _updateNotificationAsync();
  }

  @override
  @pragma('vm:entry-point')
  Future<void> onDestroy(DateTime timestamp, bool isTimeout) async {
    debugPrint("ForegroundTask: onDestroy (timeout: $isTimeout)");
  }

  @pragma('vm:entry-point')
  void _updateNotificationAsync() {
    () async {
      try {
        final url = await FlutterForegroundTask.getData<String>(key: 'backend_url');
        final token = await FlutterForegroundTask.getData<String>(key: 'access_token');
        
        if (url == null || token == null) {
          debugPrint("ForegroundTask: Credentials missing");
          return;
        }

        final response = await http.get(
          Uri.parse('$url/api/v1/finance/mobile-summary'),
          headers: {'Authorization': 'Bearer $token'},
        ).timeout(const Duration(seconds: 15));

        if (response.statusCode == 200) {
          final data = jsonDecode(response.body);
          final today = (data['today_total'] ?? 0.0).toStringAsFixed(0);
          final month = (data['monthly_total'] ?? 0.0).toStringAsFixed(0);
          
          final time = DateTime.now();
          final timeStr = "${time.hour.toString().padLeft(2, '0')}:${time.minute.toString().padLeft(2, '0')}";

          await FlutterForegroundTask.updateService(
            notificationTitle: 'WealthFam Guard',
            notificationText: 'Today: ₹$today • Month: ₹$month\nLast Updated: $timeStr',
          );
        } else {
          debugPrint("ForegroundTask: Server error ${response.statusCode}");
        }
      } catch (e) {
        debugPrint("ForegroundTask: Update error: $e");
      }
    }();
  }
}
