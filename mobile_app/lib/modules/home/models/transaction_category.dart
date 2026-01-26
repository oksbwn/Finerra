class TransactionCategory {
  final String id;
  final String name;
  final String? icon;
  final String type;

  TransactionCategory({
    required this.id,
    required this.name,
    this.icon,
    required this.type,
  });

  factory TransactionCategory.fromJson(Map<String, dynamic> json) {
    return TransactionCategory(
      id: json['id'],
      name: json['name'],
      icon: json['icon'],
      type: json['type'] ?? 'expense',
    );
  }
}
