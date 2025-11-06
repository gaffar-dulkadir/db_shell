# Chat Marketplace Service - REST API Documentation

Bu dokümantasyon Chat Marketplace Service'in tüm REST API endpoint'lerini içerir.

Base URL: `http://localhost:8080`

## İçindekiler

1. [Health](#health)
2. [Users](#users)
3. [User Profiles](#user-profiles)
4. [User Settings](#user-settings)
5. [Conversations](#conversations)
6. [Messages](#messages)
7. [Documents](#documents)
8. [Memory History](#memory-history)
9. [Bot Categories](#bot-categories)
10. [Bots](#bots)

---

## Health

### Health Check

Servislerin sağlık durumunu kontrol eder.

**GET** `/health`

```bash
curl -X GET "http://localhost:8080/health"
```

**Response:**
```json
{
  "status": "healthy",
  "service": "Chat Marketplace Service",
  "version": "2.0.0",
  "database": {
    "status": "healthy"
  }
}
```

---

## Users

### Register User

Yeni kullanıcı kaydı oluşturur.

**POST** `/users/register`

```bash
curl -X POST "http://localhost:8080/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123",
    "user_name": "John",
    "user_surname": "Doe",
    "username": "johndoe",
    "phone_number": "+905551234567"
  }'
```

**Request Body:**
```json
{
  "email": "string",
  "password": "string",
  "user_name": "string",
  "user_surname": "string",
  "username": "string",
  "phone_number": "string"
}
```

**Response:**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "user_name": "John",
  "user_surname": "Doe",
  "username": "johndoe",
  "phone_number": "+905551234567",
  "is_verified": false,
  "status": "active",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z",
  "last_login_at": null
}
```

### Login User

Kullanıcı girişi yapar.

**POST** `/users/login`

```bash
curl -X POST "http://localhost:8080/users/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

**Request Body:**
```json
{
  "email": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "user_name": "John",
  "user_surname": "Doe",
  "username": "johndoe",
  "phone_number": "+905551234567",
  "is_verified": false,
  "status": "active",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z",
  "last_login_at": "2024-01-01T12:00:00Z"
}
```

### Get Current User

Mevcut kullanıcı bilgilerini profil ve ayarları ile birlikte getirir.

**GET** `/users/me`

```bash
curl -X GET "http://localhost:8080/users/me?user_id=550e8400-e29b-41d4-a716-446655440000"
```

**Query Parameters:**
- `user_id` (string, required): Kullanıcı ID'si

**Response:**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "user_name": "John",
  "user_surname": "Doe",
  "username": "johndoe",
  "phone_number": "+905551234567",
  "is_verified": false,
  "status": "active",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z",
  "last_login_at": "2024-01-01T12:00:00Z",
  "profile": {
    "profile_id": "profile-id",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "first_name": "John",
    "last_name": "Doe",
    "display_name": "John Doe",
    "bio": "Software Developer",
    "avatar_url": "https://example.com/avatar.jpg",
    "date_of_birth": "1990-01-01T00:00:00Z",
    "location": "Istanbul, Turkey",
    "website": "https://johndoe.com",
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z"
  },
  "settings": {
    "settings_id": "settings-id",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "language": "en",
    "timezone": "UTC",
    "email_notifications": true,
    "push_notifications": true,
    "privacy_level": "public",
    "theme": "light",
    "two_factor_enabled": false,
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z"
  }
}
```

### Get User Statistics

Kullanıcı istatistiklerini getirir.

**GET** `/users/stats`

```bash
curl -X GET "http://localhost:8080/users/stats"
```

**Response:**
```json
{
  "total_users": 1000,
  "active_users": 950,
  "verified_users": 800,
  "new_users_today": 10
}
```

### Get User by ID

Belirli bir kullanıcıyı getirir.

**GET** `/users/{user_id}`

```bash
curl -X GET "http://localhost:8080/users/550e8400-e29b-41d4-a716-446655440000"
```

**Response:**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "user_name": "John",
  "user_surname": "Doe",
  "username": "johndoe",
  "phone_number": "+905551234567",
  "is_verified": false,
  "status": "active",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z",
  "last_login_at": "2024-01-01T12:00:00Z"
}
```

### Update User

Kullanıcı bilgilerini günceller.

**PUT** `/users/{user_id}`

```bash
curl -X PUT "http://localhost:8080/users/550e8400-e29b-41d4-a716-446655440000" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johnsmith",
    "phone_number": "+905559876543",
    "status": "active"
  }'
```

**Request Body:**
```json
{
  "username": "string",
  "phone_number": "string",
  "status": "active|inactive|suspended"
}
```

### Change Password

Kullanıcı şifresini değiştirir.

**POST** `/users/{user_id}/change-password`

```bash
curl -X POST "http://localhost:8080/users/550e8400-e29b-41d4-a716-446655440000/change-password" \
  -H "Content-Type: application/json" \
  -d '{
    "current_password": "oldpassword123",
    "new_password": "newpassword123"
  }'
```

**Request Body:**
```json
{
  "current_password": "string",
  "new_password": "string"
}
```

**Response:**
```json
{
  "message": "Password changed successfully"
}
```

### Verify Email

Kullanıcının e-postasını doğrular.

**POST** `/users/{user_id}/verify-email`

```bash
curl -X POST "http://localhost:8080/users/550e8400-e29b-41d4-a716-446655440000/verify-email"
```

**Response:**
```json
{
  "message": "Email verified successfully"
}
```

### Deactivate User

Kullanıcı hesabını deaktive eder.

**POST** `/users/{user_id}/deactivate`

```bash
curl -X POST "http://localhost:8080/users/550e8400-e29b-41d4-a716-446655440000/deactivate"
```

**Response:**
```json
{
  "message": "User deactivated successfully"
}
```

### Search Users

Kullanıcıları filtreler ve arar.

**GET** `/users/`

```bash
curl -X GET "http://localhost:8080/users/?query=john&status=active&limit=20&offset=0"
```

**Query Parameters:**
- `query` (string, optional): Arama sorgusu
- `status` (string, optional): Durum filtresi (active/inactive/suspended)
- `limit` (integer, optional): Döndürülecek kullanıcı sayısı (default: 20, max: 200)
- `offset` (integer, optional): Atlanacak kullanıcı sayısı (default: 0)

**Response:**
```json
{
  "users": [
    {
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "email": "user@example.com",
      "user_name": "John",
      "user_surname": "Doe",
      "username": "johndoe",
      "phone_number": "+905551234567",
      "is_verified": false,
      "status": "active",
      "created_at": "2024-01-01T12:00:00Z",
      "updated_at": "2024-01-01T12:00:00Z",
      "last_login_at": "2024-01-01T12:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 20,
  "has_next": false,
  "has_prev": false
}
```

---

## User Profiles

### Create User Profile

Kullanıcı profili oluşturur.

**POST** `/users/{user_id}/profile`

```bash
curl -X POST "http://localhost:8080/users/550e8400-e29b-41d4-a716-446655440000/profile" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "display_name": "John Doe",
    "bio": "Software Developer",
    "avatar_url": "https://example.com/avatar.jpg",
    "date_of_birth": "1990-01-01T00:00:00Z",
    "location": "Istanbul, Turkey",
    "website": "https://johndoe.com"
  }'
```

**Request Body:**
```json
{
  "first_name": "string",
  "last_name": "string",
  "display_name": "string",
  "bio": "string",
  "avatar_url": "string",
  "date_of_birth": "2024-01-01T00:00:00Z",
  "location": "string",
  "website": "string"
}
```

### Get User Profile

Kullanıcı profilini getirir.

**GET** `/users/{user_id}/profile`

```bash
curl -X GET "http://localhost:8080/users/550e8400-e29b-41d4-a716-446655440000/profile"
```

**Response:**
```json
{
  "profile_id": "profile-id",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "first_name": "John",
  "last_name": "Doe",
  "display_name": "John Doe",
  "bio": "Software Developer",
  "avatar_url": "https://example.com/avatar.jpg",
  "date_of_birth": "1990-01-01T00:00:00Z",
  "location": "Istanbul, Turkey",
  "website": "https://johndoe.com",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

### Update User Profile

Kullanıcı profilini günceller.

**PUT** `/users/{user_id}/profile`

```bash
curl -X PUT "http://localhost:8080/users/550e8400-e29b-41d4-a716-446655440000/profile" \
  -H "Content-Type: application/json" \
  -d '{
    "bio": "Senior Software Developer",
    "location": "Ankara, Turkey"
  }'
```

### Update Avatar

Kullanıcı avatar'ını günceller.

**PATCH** `/users/{user_id}/profile/avatar`

```bash
curl -X PATCH "http://localhost:8080/users/550e8400-e29b-41d4-a716-446655440000/profile/avatar?avatar_url=https://example.com/new-avatar.jpg"
```

**Query Parameters:**
- `avatar_url` (string, required): Yeni avatar URL'si

### Delete User Profile

Kullanıcı profilini siler.

**DELETE** `/users/{user_id}/profile`

```bash
curl -X DELETE "http://localhost:8080/users/550e8400-e29b-41d4-a716-446655440000/profile"
```

**Response:**
```json
{
  "message": "Profile deleted successfully"
}
```

### Search Profiles

Profilleri ada göre arar.

**GET** `/profiles/search`

```bash
curl -X GET "http://localhost:8080/profiles/search?query=john&limit=20&offset=0"
```

**Query Parameters:**
- `query` (string, required): Arama sorgusu
- `limit` (integer, optional): Döndürülecek profil sayısı (default: 20, max: 200)
- `offset` (integer, optional): Atlanacak profil sayısı (default: 0)

**Response:**
```json
[
  {
    "profile_id": "profile-id",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "first_name": "John",
    "last_name": "Doe",
    "display_name": "John Doe",
    "bio": "Software Developer",
    "avatar_url": "https://example.com/avatar.jpg",
    "date_of_birth": "1990-01-01T00:00:00Z",
    "location": "Istanbul, Turkey",
    "website": "https://johndoe.com",
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z"
  }
]
```

---

## User Settings

### Create User Settings

Kullanıcı ayarları oluşturur.

**POST** `/users/{user_id}/settings`

```bash
curl -X POST "http://localhost:8080/users/550e8400-e29b-41d4-a716-446655440000/settings" \
  -H "Content-Type: application/json" \
  -d '{
    "language": "tr",
    "timezone": "Europe/Istanbul",
    "email_notifications": true,
    "push_notifications": false,
    "privacy_level": "private",
    "theme": "dark",
    "two_factor_enabled": true
  }'
```

**Request Body:**
```json
{
  "language": "string",
  "timezone": "string",
  "email_notifications": true,
  "push_notifications": true,
  "privacy_level": "string",
  "theme": "string",
  "two_factor_enabled": false
}
```

### Get User Settings

Kullanıcı ayarlarını getirir.

**GET** `/users/{user_id}/settings`

```bash
curl -X GET "http://localhost:8080/users/550e8400-e29b-41d4-a716-446655440000/settings"
```

**Response:**
```json
{
  "settings_id": "settings-id",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "language": "en",
  "timezone": "UTC",
  "email_notifications": true,
  "push_notifications": true,
  "privacy_level": "public",
  "theme": "light",
  "two_factor_enabled": false,
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

### Update User Settings

Kullanıcı ayarlarını günceller.

**PUT** `/users/{user_id}/settings`

```bash
curl -X PUT "http://localhost:8080/users/550e8400-e29b-41d4-a716-446655440000/settings" \
  -H "Content-Type: application/json" \
  -d '{
    "theme": "dark",
    "language": "tr"
  }'
```

### Update Notification Settings

Bildirim ayarlarını günceller.

**PATCH** `/users/{user_id}/settings/notifications`

```bash
curl -X PATCH "http://localhost:8080/users/550e8400-e29b-41d4-a716-446655440000/settings/notifications?email_notifications=false&push_notifications=true"
```

**Query Parameters:**
- `email_notifications` (boolean, optional): E-posta bildirimlerini etkinleştir
- `push_notifications` (boolean, optional): Push bildirimlerini etkinleştir

### Update Theme

Tema ayarını günceller.

**PATCH** `/users/{user_id}/settings/theme`

```bash
curl -X PATCH "http://localhost:8080/users/550e8400-e29b-41d4-a716-446655440000/settings/theme?theme=dark"
```

**Query Parameters:**
- `theme` (string, required): Tema adı (light, dark)

### Update Language

Dil ayarını günceller.

**PATCH** `/users/{user_id}/settings/language`

```bash
curl -X PATCH "http://localhost:8080/users/550e8400-e29b-41d4-a716-446655440000/settings/language?language=tr"
```

**Query Parameters:**
- `language` (string, required): Dil kodu (en, tr)

### Toggle Two-Factor Authentication

İki faktörlü kimlik doğrulamayı açar/kapatır.

**PATCH** `/users/{user_id}/settings/two-factor`

```bash
curl -X PATCH "http://localhost:8080/users/550e8400-e29b-41d4-a716-446655440000/settings/two-factor?enabled=true"
```

**Query Parameters:**
- `enabled` (boolean, required): İki faktörlü kimlik doğrulamayı etkinleştir

### Reset Settings

Ayarları varsayılan değerlere sıfırlar.

**POST** `/users/{user_id}/settings/reset`

```bash
curl -X POST "http://localhost:8080/users/550e8400-e29b-41d4-a716-446655440000/settings/reset"
```

### Delete User Settings

Kullanıcı ayarlarını siler.

**DELETE** `/users/{user_id}/settings`

```bash
curl -X DELETE "http://localhost:8080/users/550e8400-e29b-41d4-a716-446655440000/settings"
```

**Response:**
```json
{
  "message": "Settings deleted successfully"
}
```

---

## Conversations

### Create Conversation

Yeni konuşma oluşturur.

**POST** `/users/{user_id}/conversations`

```bash
curl -X POST "http://localhost:8080/users/550e8400-e29b-41d4-a716-446655440000/conversations" \
  -H "Content-Type: application/json" \
  -d '{
    "bot_id": "bot-id-123",
    "title": "AI Assistant Chat",
    "description": "Chat with AI assistant about coding",
    "metadata": {
      "tags": ["programming", "help"]
    }
  }'
```

**Request Body:**
```json
{
  "bot_id": "string",
  "title": "string",
  "description": "string",
  "metadata": {}
}
```

**Response:**
```json
{
  "conversation_id": "conv-id-123",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "bot_id": "bot-id-123",
  "title": "AI Assistant Chat",
  "description": "Chat with AI assistant about coding",
  "status": "active",
  "metadata": {
    "tags": ["programming", "help"]
  },
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z",
  "last_message_at": null,
  "message_count": 0
}
```

### Get User Conversations

Kullanıcının konuşmalarını getirir.

**GET** `/users/{user_id}/conversations`

```bash
curl -X GET "http://localhost:8080/users/550e8400-e29b-41d4-a716-446655440000/conversations?status=active&limit=20&offset=0"
```

**Query Parameters:**
- `status` (string, optional): Konuşma durumu filtresi (active/archived/deleted)
- `limit` (integer, optional): Döndürülecek konuşma sayısı (default: 20, max: 200)
- `offset` (integer, optional): Atlanacak konuşma sayısı (default: 0)

**Response:**
```json
{
  "conversations": [
    {
      "conversation_id": "conv-id-123",
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "bot_id": "bot-id-123",
      "title": "AI Assistant Chat",
      "description": "Chat with AI assistant about coding",
      "status": "active",
      "metadata": {},
      "created_at": "2024-01-01T12:00:00Z",
      "updated_at": "2024-01-01T12:00:00Z",
      "last_message_at": "2024-01-01T12:30:00Z",
      "message_count": 5
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 20,
  "has_next": false,
  "has_prev": false
}
```

### Get Conversation

Belirli bir konuşmayı getirir.

**GET** `/users/{user_id}/conversations/{conversation_id}`

```bash
curl -X GET "http://localhost:8080/users/550e8400-e29b-41d4-a716-446655440000/conversations/conv-id-123?include_messages=false"
```

**Query Parameters:**
- `include_messages` (boolean, optional): Son mesajları dahil et (default: false)

### Update Conversation

Konuşmayı günceller.

**PUT** `/users/{user_id}/conversations/{conversation_id}`

```bash
curl -X PUT "http://localhost:8080/users/550e8400-e29b-41d4-a716-446655440000/conversations/conv-id-123" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Chat Title",
    "description": "Updated description"
  }'
```

### Archive Conversation

Konuşmayı arşivler.

**POST** `/users/{user_id}/conversations/{conversation_id}/archive`

```bash
curl -X POST "http://localhost:8080/users/550e8400-e29b-41d4-a716-446655440000/conversations/conv-id-123/archive"
```

**Response:**
```json
{
  "message": "Conversation archived successfully"
}
```

### Restore Conversation

Arşivlenmiş konuşmayı geri yükler.

**POST** `/users/{user_id}/conversations/{conversation_id}/restore`

```bash
curl -X POST "http://localhost:8080/users/550e8400-e29b-41d4-a716-446655440000/conversations/conv-id-123/restore"
```

### Delete Conversation

Konuşmayı siler (soft delete).

**DELETE** `/users/{user_id}/conversations/{conversation_id}`

```bash
curl -X DELETE "http://localhost:8080/users/550e8400-e29b-41d4-a716-446655440000/conversations/conv-id-123"
```

### Search Conversations

Konuşmaları filtreler ile arar.

**GET** `/users/{user_id}/conversations/search`

```bash
curl -X GET "http://localhost:8080/users/550e8400-e29b-41d4-a716-446655440000/conversations/search?query=AI&status=active&bot_id=bot-id-123&start_date=2024-01-01T00:00:00Z&end_date=2024-12-31T23:59:59Z&limit=20&offset=0"
```

**Query Parameters:**
- `query` (string, optional): Arama sorgusu
- `status` (string, optional): Durum filtresi
- `bot_id` (string, optional): Bot ID filtresi
- `start_date` (string, optional): Başlangıç tarihi (ISO format)
- `end_date` (string, optional): Bitiş tarihi (ISO format)
- `limit` (integer, optional): Döndürülecek konuşma sayısı
- `offset` (integer, optional): Atlanacak konuşma sayısı

### Get Recent Conversations

Son konuşmaları getirir.

**GET** `/users/{user_id}/conversations/recent`

```bash
curl -X GET "http://localhost:8080/users/550e8400-e29b-41d4-a716-446655440000/conversations/recent?days=7&limit=10"
```

**Query Parameters:**
- `days` (integer, optional): Kaç gün geriye bakılacak (default: 7, max: 30)
- `limit` (integer, optional): Döndürülecek konuşma sayısı (default: 10, max: 50)

### Get Conversation Statistics

Konuşma istatistiklerini getirir.

**GET** `/users/{user_id}/conversations/stats`

```bash
curl -X GET "http://localhost:8080/users/550e8400-e29b-41d4-a716-446655440000/conversations/stats"
```

**Response:**
```json
{
  "total_conversations": 25,
  "active_conversations": 20,
  "archived_conversations": 5,
  "total_messages": 150,
  "today_messages": 10,
  "avg_messages_per_conversation": 6.0
}
```

---

## Messages

### Create Message

Konuşmada yeni mesaj oluşturur.

**POST** `/users/{user_id}/conversations/{conversation_id}/messages`

```bash
curl -X POST "http://localhost:8080/users/550e8400-e29b-41d4-a716-446655440000/conversations/conv-id-123/messages" \
  -H "Content-Type: application/json" \
  -d '{
    "sender_type": "user",
    "sender_id": "550e8400-e29b-41d4-a716-446655440000",
    "message_type": "text",
    "content": "Hello, how can I help you?",
    "metadata": {
      "platform": "web"
    }
  }'
```

**Request Body:**
```json
{
  "sender_type": "user|bot",
  "sender_id": "string",
  "message_type": "text|image|document|audio|video|system",
  "content": "string",
  "metadata": {}
}
```

**Response:**
```json
{
  "message_id": "msg-id-123",
  "conversation_id": "conv-id-123",
  "parent_message_id": null,
  "sender_type": "user",
  "sender_id": "550e8400-e29b-41d4-a716-446655440000",
  "message_type": "text",
  "content": "Hello, how can I help you?",
  "metadata": {},
  "is_edited": false,
  "is_deleted": false,
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

### Get Conversation Messages

Konuşmanın mesajlarını getirir.

**GET** `/users/{user_id}/conversations/{conversation_id}/messages`

```bash
curl -X GET "http://localhost:8080/users/550e8400-e29b-41d4-a716-446655440000/conversations/conv-id-123/messages?limit=50&offset=0&include_deleted=false"
```

**Query Parameters:**
- `limit` (integer, optional): Döndürülecek mesaj sayısı (default: 50, max: 200)
- `offset` (integer, optional): Atlanacak mesaj sayısı (default: 0)
- `include_deleted` (boolean, optional): Silinmiş mesajları dahil et (default: false)

**Response:**
```json
{
  "messages": [
    {
      "message_id": "msg-id-123",
      "conversation_id": "conv-id-123",
      "parent_message_id": null,
      "sender_type": "user",
      "sender_id": "550e8400-e29b-41d4-a716-446655440000",
      "message_type": "text",
      "content": "Hello, how can I help you?",
      "metadata": {},
      "is_edited": false,
      "is_deleted": false,
      "created_at": "2024-01-01T12:00:00Z",
      "updated_at": "2024-01-01T12:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 50,
  "has_next": false,
  "has_prev": false
}
```

### Get Message

Belirli bir mesajı getirir.

**GET** `/users/{user_id}/conversations/{conversation_id}/messages/{message_id}`

```bash
curl -X GET "http://localhost:8080/users/550e8400-e29b-41d4-a716-446655440000/conversations/conv-id-123/messages/msg-id-123?include_documents=false"
```

**Query Parameters:**
- `include_documents` (boolean, optional): Mesaj belgelerini dahil et (default: false)

### Update Message

Mesajı günceller.

**PUT** `/users/{user_id}/conversations/{conversation_id}/messages/{message_id}`

```bash
curl -X PUT "http://localhost:8080/users/550e8400-e29b-41d4-a716-446655440000/conversations/conv-id-123/messages/msg-id-123" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Updated message content",
    "is_edited": true
  }'
```

**Request Body:**
```json
{
  "content": "string",
  "metadata": {},
  "is_edited": true
}
```

### Delete Message

Mesajı siler (soft delete).

**DELETE** `/users/{user_id}/conversations/{conversation_id}/messages/{message_id}`

```bash
curl -X DELETE "http://localhost:8080/users/550e8400-e29b-41d4-a716-446655440000/conversations/conv-id-123/messages/msg-id-123"
```

**Response:**
```json
{
  "message": "Message deleted successfully"
}
```

### Search Messages

Konuşmadaki mesajları arar.

**GET** `/users/{user_id}/conversations/{conversation_id}/messages/search`

```bash
curl -X GET "http://localhost:8080/users/550e8400-e29b-41d4-a716-446655440000/conversations/conv-id-123/messages/search?query=hello&message_type=text&sender_type=user&start_date=2024-01-01T00:00:00Z&end_date=2024-12-31T23:59:59Z&limit=20&offset=0"
```

**Query Parameters:**
- `query` (string, optional): Arama sorgusu
- `message_type` (string, optional): Mesaj türü filtresi
- `sender_type` (string, optional): Gönderen türü filtresi (user/bot)
- `start_date` (string, optional): Başlangıç tarihi (ISO format)
- `end_date` (string, optional): Bitiş tarihi (ISO format)
- `limit` (integer, optional): Döndürülecek mesaj sayısı
- `offset` (integer, optional): Atlanacak mesaj sayısı

### Get Recent Messages

Son mesajları getirir.

**GET** `/users/{user_id}/conversations/{conversation_id}/messages/recent`

```bash
curl -X GET "http://localhost:8080/users/550e8400-e29b-41d4-a716-446655440000/conversations/conv-id-123/messages/recent?hours=24&limit=50"
```

**Query Parameters:**
- `hours` (integer, optional): Kaç saat geriye bakılacak (default: 24, max: 168)
- `limit` (integer, optional): Döndürülecek mesaj sayısı (default: 50, max: 200)

### Get Message Statistics

Mesaj istatistiklerini getirir.

**GET** `/users/{user_id}/conversations/{conversation_id}/messages/stats`

```bash
curl -X GET "http://localhost:8080/users/550e8400-e29b-41d4-a716-446655440000/conversations/conv-id-123/messages/stats"
```

**Response:**
```json
{
  "total_messages": 100,
  "user_messages": 60,
  "bot_messages": 40,
  "today_messages": 5,
  "message_types": {
    "text": 80,
    "image": 15,
    "document": 5
  },
  "avg_message_length": 125.5
}
```

---

## Documents

### Add Document to Message

Mesaja belge ekler.

**POST** `/users/{user_id}/conversations/{conversation_id}/messages/{message_id}/documents`

```bash
curl -X POST "http://localhost:8080/users/550e8400-e29b-41d4-a716-446655440000/conversations/conv-id-123/messages/msg-id-123/documents" \
  -H "Content-Type: application/json" \
  -d '{
    "file_name": "document.pdf",
    "file_type": "pdf",
    "file_size": 1024567,
    "file_url": "https://example.com/documents/document.pdf",
    "mime_type": "application/pdf",
    "metadata": {
      "description": "Important document"
    }
  }'
```

**Request Body:**
```json
{
  "file_name": "string",
  "file_type": "string",
  "file_size": 1024,
  "file_url": "string",
  "mime_type": "string",
  "metadata": {}
}
```

**Response:**
```json
{
  "document_id": "doc-id-123",
  "message_id": "msg-id-123",
  "file_name": "document.pdf",
  "file_type": "pdf",
  "file_size": 1024567,
  "file_url": "https://example.com/documents/document.pdf",
  "mime_type": "application/pdf",
  "metadata": {},
  "created_at": "2024-01-01T12:00:00Z"
}
```

### Get Message Documents

Mesajın belgelerini getirir.

**GET** `/users/{user_id}/conversations/{conversation_id}/messages/{message_id}/documents`

```bash
curl -X GET "http://localhost:8080/users/550e8400-e29b-41d4-a716-446655440000/conversations/conv-id-123/messages/msg-id-123/documents"
```

**Response:**
```json
[
  {
    "document_id": "doc-id-123",
    "message_id": "msg-id-123",
    "file_name": "document.pdf",
    "file_type": "pdf",
    "file_size": 1024567,
    "file_url": "https://example.com/documents/document.pdf",
    "mime_type": "application/pdf",
    "metadata": {},
    "created_at": "2024-01-01T12:00:00Z"
  }
]
```

### Get Conversation Documents

Konuşmanın tüm belgelerini getirir.

**GET** `/users/{user_id}/conversations/{conversation_id}/documents`

```bash
curl -X GET "http://localhost:8080/users/550e8400-e29b-41d4-a716-446655440000/conversations/conv-id-123/documents?limit=100&offset=0"
```

**Query Parameters:**
- `limit` (integer, optional): Döndürülecek belge sayısı (default: 100, max: 200)
- `offset` (integer, optional): Atlanacak belge sayısı (default: 0)

**Response:**
```json
{
  "documents": [
    {
      "document_id": "doc-id-123",
      "message_id": "msg-id-123",
      "file_name": "document.pdf",
      "file_type": "pdf",
      "file_size": 1024567,
      "file_url": "https://example.com/documents/document.pdf",
      "mime_type": "application/pdf",
      "metadata": {},
      "created_at": "2024-01-01T12:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 100,
  "has_next": false,
  "has_prev": false
}
```

---

## Memory History

### Add Memory

Konuşmaya hafıza girdisi ekler.

**POST** `/users/{user_id}/conversations/{conversation_id}/memory-history`

```bash
curl -X POST "http://localhost:8080/users/550e8400-e29b-41d4-a716-446655440000/conversations/conv-id-123/memory-history" \
  -H "Content-Type: application/json" \
  -d '{
    "memory_key": "user_preference",
    "memory_value": "User prefers concise answers",
    "memory_type": "context",
    "priority": 5,
    "expires_at": "2024-12-31T23:59:59Z"
  }'
```

**Request Body:**
```json
{
  "memory_key": "string",
  "memory_value": "string",
  "memory_type": "string",
  "priority": 1,
  "expires_at": "2024-01-01T00:00:00Z"
}
```

**Response:**
```json
{
  "memory_id": "mem-id-123",
  "conversation_id": "conv-id-123",
  "memory_key": "user_preference",
  "memory_value": "User prefers concise answers",
  "memory_type": "context",
  "priority": 5,
  "expires_at": "2024-12-31T23:59:59Z",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

### Get Conversation Memories

Konuşmanın hafıza girdilerini getirir.

**GET** `/users/{user_id}/conversations/{conversation_id}/memory-history`

```bash
curl -X GET "http://localhost:8080/users/550e8400-e29b-41d4-a716-446655440000/conversations/conv-id-123/memory-history?memory_type=context&limit=100&offset=0"
```

**Query Parameters:**
- `memory_type` (string, optional): Hafıza türü filtresi
- `limit` (integer, optional): Döndürülecek hafıza sayısı (default: 100, max: 200)
- `offset` (integer, optional): Atlanacak hafıza sayısı (default: 0)

**Response:**
```json
{
  "memories": [
    {
      "memory_id": "mem-id-123",
      "conversation_id": "conv-id-123",
      "memory_key": "user_preference",
      "memory_value": "User prefers concise answers",
      "memory_type": "context",
      "priority": 5,
      "expires_at": "2024-12-31T23:59:59Z",
      "created_at": "2024-01-01T12:00:00Z",
      "updated_at": "2024-01-01T12:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 100,
  "has_next": false,
  "has_prev": false
}
```

---

## Bot Categories

### Create Bot Category

Yeni bot kategorisi oluşturur (admin only).

**POST** `/marketplace/bot-categories`

```bash
curl -X POST "http://localhost:8080/marketplace/bot-categories" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "AI Assistants",
    "description": "General purpose AI assistants",
    "icon": "🤖",
    "color": "#007bff",
    "is_active": true,
    "sort_order": 1
  }'
```

**Request Body:**
```json
{
  "name": "string",
  "description": "string",
  "icon": "string",
  "color": "#007bff",
  "is_active": true,
  "sort_order": 0
}
```

**Response:**
```json
{
  "category_id": "cat-id-123",
  "name": "AI Assistants",
  "description": "General purpose AI assistants",
  "icon": "🤖",
  "color": "#007bff",
  "is_active": true,
  "sort_order": 1,
  "bot_count": 0,
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

### Get Active Categories

Aktif bot kategorilerini getirir.

**GET** `/marketplace/bot-categories`

```bash
curl -X GET "http://localhost:8080/marketplace/bot-categories?limit=100&offset=0"
```

**Query Parameters:**
- `limit` (integer, optional): Döndürülecek kategori sayısı (default: 100, max: 200)
- `offset` (integer, optional): Atlanacak kategori sayısı (default: 0)

**Response:**
```json
[
  {
    "category_id": "cat-id-123",
    "name": "AI Assistants",
    "description": "General purpose AI assistants",
    "icon": "🤖",
    "color": "#007bff",
    "is_active": true,
    "sort_order": 1,
    "bot_count": 5,
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z"
  }
]
```

### Get Category

Belirli bir kategoriyi getirir.

**GET** `/marketplace/bot-categories/{category_id}`

```bash
curl -X GET "http://localhost:8080/marketplace/bot-categories/cat-id-123"
```

### Search Categories

Kategorileri filtreler ile arar.

**GET** `/marketplace/bot-categories/search`

```bash
curl -X GET "http://localhost:8080/marketplace/bot-categories/search?query=AI&is_active=true&has_bots=true&sort_by=sort_order&sort_order=asc&limit=20&offset=0"
```

**Query Parameters:**
- `query` (string, optional): Arama sorgusu
- `is_active` (boolean, optional): Aktif durum filtresi
- `has_bots` (boolean, optional): Bot içeren kategoriler
- `sort_by` (string, optional): Sıralama alanı (default: sort_order)
- `sort_order` (string, optional): Sıralama düzeni (asc, desc)
- `limit` (integer, optional): Döndürülecek kategori sayısı
- `offset` (integer, optional): Atlanacak kategori sayısı

---

## Bots

### Create Bot

Yeni bot oluşturur.

**POST** `/marketplace/bots`

```bash
curl -X POST "http://localhost:8080/marketplace/bots?created_by=550e8400-e29b-41d4-a716-446655440000" \
  -H "Content-Type: application/json" \
  -d '{
    "category_id": "cat-id-123",
    "name": "chatgpt",
    "display_name": "ChatGPT Assistant",
    "description": "A powerful AI assistant for various tasks",
    "avatar_url": "https://example.com/avatars/chatgpt.png",
    "is_featured": false,
    "is_premium": true,
    "capabilities": {
      "text_generation": true,
      "code_assistance": true,
      "translations": true
    },
    "configuration": {
      "model": "gpt-4",
      "temperature": 0.7,
      "max_tokens": 2000
    }
  }'
```

**Query Parameters:**
- `created_by` (string, optional): Oluşturan kullanıcının ID'si

**Request Body:**
```json
{
  "category_id": "string",
  "name": "string",
  "display_name": "string",
  "description": "string",
  "avatar_url": "string",
  "is_featured": false,
  "is_premium": false,
  "capabilities": {},
  "configuration": {}
}
```

**Response:**
```json
{
  "bot_id": "bot-id-123",
  "category_id": "cat-id-123",
  "name": "chatgpt",
  "display_name": "ChatGPT Assistant",
  "description": "A powerful AI assistant for various tasks",
  "avatar_url": "https://example.com/avatars/chatgpt.png",
  "status": "pending",
  "is_featured": false,
  "is_premium": true,
  "rating": null,
  "total_conversations": 0,
  "capabilities": {},
  "configuration": {},
  "created_by": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

### Search Bots

Gelişmiş filtreler ile bot arar.

**GET** `/marketplace/bots`

```bash
curl -X GET "http://localhost:8080/marketplace/bots?query=assistant&category_id=cat-id-123&status=active&is_featured=true&is_premium=false&min_rating=4.0&sort_by=rating&sort_order=desc&limit=20&offset=0"
```

**Query Parameters:**
- `query` (string, optional): Arama sorgusu
- `category_id` (string, optional): Kategori filtresi
- `status` (string, optional): Durum filtresi (active/inactive/pending/rejected)
- `is_featured` (boolean, optional): Öne çıkan bot filtresi
- `is_premium` (boolean, optional): Premium bot filtresi
- `min_rating` (float, optional): Minimum puan (0-5)
- `sort_by` (string, optional): Sıralama alanı (default: name)
- `sort_order` (string, optional): Sıralama düzeni (asc, desc)
- `limit` (integer, optional): Döndürülecek bot sayısı
- `offset` (integer, optional): Atlanacak bot sayısı

**Response:**
```json
{
  "bots": [
    {
      "bot_id": "bot-id-123",
      "category_id": "cat-id-123",
      "name": "chatgpt",
      "display_name": "ChatGPT Assistant",
      "description": "A powerful AI assistant for various tasks",
      "avatar_url": "https://example.com/avatars/chatgpt.png",
      "status": "active",
      "is_featured": true,
      "is_premium": true,
      "rating": 4.8,
      "total_conversations": 1250,
      "capabilities": {},
      "configuration": {},
      "created_by": "550e8400-e29b-41d4-a716-446655440000",
      "created_at": "2024-01-01T12:00:00Z",
      "updated_at": "2024-01-01T12:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 20,
  "has_next": false,
  "has_prev": false
}
```

### Get Bot Detail

Detaylı bot bilgilerini getirir.

**GET** `/marketplace/bots/{bot_id}`

```bash
curl -X GET "http://localhost:8080/marketplace/bots/bot-id-123"
```

**Response:**
```json
{
  "bot_id": "bot-id-123",
  "category_id": "cat-id-123",
  "name": "chatgpt",
  "display_name": "ChatGPT Assistant",
  "description": "A powerful AI assistant for various tasks",
  "avatar_url": "https://example.com/avatars/chatgpt.png",
  "status": "active",
  "is_featured": true,
  "is_premium": true,
  "rating": 4.8,
  "total_conversations": 1250,
  "capabilities": {},
  "configuration": {},
  "created_by": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z",
  "category": {
    "category_id": "cat-id-123",
    "name": "AI Assistants",
    "description": "General purpose AI assistants",
    "icon": "🤖",
    "color": "#007bff",
    "is_active": true,
    "sort_order": 1,
    "bot_count": 5,
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z"
  },
  "conversation_count": 1250,
  "recent_conversations": 125
}
```

### Get Bot by Name

Bot adıyla bot getirir.

**GET** `/marketplace/bots/name/{bot_name}`

```bash
curl -X GET "http://localhost:8080/marketplace/bots/name/chatgpt"
```

### Update Bot

Bot bilgilerini günceller.

**PUT** `/marketplace/bots/{bot_id}`

```bash
curl -X PUT "http://localhost:8080/marketplace/bots/bot-id-123" \
  -H "Content-Type: application/json" \
  -d '{
    "display_name": "Updated ChatGPT Assistant",
    "description": "Updated description",
    "is_featured": true
  }'
```

### Get Bots by Category

Belirli kategorideki botları getirir.

**GET** `/marketplace/bots/category/{category_id}`

```bash
curl -X GET "http://localhost:8080/marketplace/bots/category/cat-id-123?status=active&limit=20&offset=0"
```

**Query Parameters:**
- `status` (string, optional): Bot durumu (default: active)
- `limit` (integer, optional): Döndürülecek bot sayısı
- `offset` (integer, optional): Atlanacak bot sayısı

### Get Featured Bots

Öne çıkan botları getirir.

**GET** `/marketplace/bots/featured`

```bash
curl -X GET "http://localhost:8080/marketplace/bots/featured?limit=10"
```

**Query Parameters:**
- `limit` (integer, optional): Döndürülecek bot sayısı (default: 10, max: 50)

### Get Top Rated Bots

En yüksek puanlı botları getirir.

**GET** `/marketplace/bots/top-rated`

```bash
curl -X GET "http://localhost:8080/marketplace/bots/top-rated?limit=10"
```

### Get Most Used Bots

En çok kullanılan botları getirir.

**GET** `/marketplace/bots/most-used`

```bash
curl -X GET "http://localhost:8080/marketplace/bots/most-used?limit=10"
```

### Approve Bot

Bot onaylar (admin only).

**POST** `/marketplace/bots/{bot_id}/approve`

```bash
curl -X POST "http://localhost:8080/marketplace/bots/bot-id-123/approve"
```

**Response:**
```json
{
  "message": "Bot approved successfully"
}
```

### Reject Bot

Bot reddeder (admin only).

**POST** `/marketplace/bots/{bot_id}/reject`

```bash
curl -X POST "http://localhost:8080/marketplace/bots/bot-id-123/reject"
```

### Update Bot Rating

Bot puanını günceller.

**PATCH** `/marketplace/bots/{bot_id}/rating`

```bash
curl -X PATCH "http://localhost:8080/marketplace/bots/bot-id-123/rating?rating=4.5"
```

**Query Parameters:**
- `rating` (float, required): Yeni puan (0-5)

**Response:**
```json
{
  "message": "Bot rating updated successfully",
  "rating": 4.5
}
```

### Get Bot Statistics

Bot pazarı istatistiklerini getirir.

**GET** `/marketplace/bots/stats`

```bash
curl -X GET "http://localhost:8080/marketplace/bots/stats"
```

**Response:**
```json
{
  "total_bots": 150,
  "active_bots": 120,
  "pending_bots": 25,
  "featured_bots": 10,
  "premium_bots": 50,
  "bots_by_category": {
    "AI Assistants": 50,
    "Code Helpers": 30,
    "Language Learning": 20,
    "Entertainment": 25,
    "Productivity": 25
  },
  "top_rated_bots": [],
  "most_used_bots": []
}
```

---

## Error Responses

Tüm API endpoint'leri standart hata yanıtları döndürür:

### 400 Bad Request
```json
{
  "detail": "Validation error message",
  "code": "VALIDATION_ERROR",
  "details": {}
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication failed",
  "code": "AUTHENTICATION_ERROR",
  "details": {}
}
```

### 403 Forbidden
```json
{
  "detail": "Access denied",
  "code": "AUTHORIZATION_ERROR",
  "details": {}
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found",
  "code": "NOT_FOUND",
  "details": {}
}
```

### 409 Conflict
```json
{
  "detail": "Resource already exists",
  "code": "DUPLICATE_ERROR",
  "details": {}
}
```

### 429 Too Many Requests
```json
{
  "detail": "Rate limit exceeded",
  "code": "RATE_LIMIT_EXCEEDED",
  "details": {}
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error",
  "code": "INTERNAL_ERROR",
  "error": "Error details (only in development)"
}
```

### 503 Service Unavailable
```json
{
  "detail": "Service temporarily unavailable",
  "code": "SERVICE_UNAVAILABLE",
  "details": {}
}
```

---

## API Root

### Get API Information

API hakkında temel bilgileri getirir.

**GET** `/`

```bash
curl -X GET "http://localhost:8080/"
```

**Response:**
```json
{
  "service": "Chat Marketplace Service",
  "version": "2.0.0",
  "description": "REST API for WhatsApp-like chat marketplace with comprehensive user, conversation, message, and bot management",
  "docs_url": "/docs",
  "health_url": "/health",
  "endpoints": {
    "users": "/users",
    "user_profiles": "/users/{user_id}/profile",
    "user_settings": "/users/{user_id}/settings",
    "conversations": "/users/{user_id}/conversations",
    "messages": "/users/{user_id}/conversations/{conversation_id}/messages",
    "documents": "/users/{user_id}/conversations/{conversation_id}/documents",
    "memory": "/users/{user_id}/conversations/{conversation_id}/memory-history",
    "bot_categories": "/marketplace/bot-categories",
    "bots": "/marketplace/bots",
    "admin": "/admin/*"
  }
}
```

---

## Notes

- Tüm timestamp'ler ISO 8601 formatında UTC olarak döndürülür
- Pagination kullanan endpoint'ler `limit` ve `offset` parametrelerini destekler
- Boolean query parametreleri `true`/`false` değerlerini kabul eder
- String enum'ları case-sensitive'dir
- File upload'lar için ayrı endpoint'ler oluşturulmalıdır
- Authentication için JWT token sistemi eklenebilir
- Rate limiting aktif olduğunda uygun header'lar döndürülür
