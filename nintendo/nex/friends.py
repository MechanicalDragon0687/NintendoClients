
from nintendo.nex import common, service
from nintendo import miis

import logging
logger = logging.getLogger(__name__)


class FriendsTitle:
	TITLE_ID_EUR = 0x10001C00
	TITLE_ID_USA = 0x10001C00
	TITLE_ID_JAP = 0x10001C00
	LATEST_VERSION = 0
	
	GAME_SERVER_ID = 0x3200
	ACCESS_KEY = "ridfebb9"
	NEX_VERSION = 20000

class FriendsTitle3DS:
	TITLE_ID_EUR = 0x0004003000009F02
	TITLE_ID_USA = 0x0004003000009602
	TITLE_ID_JAP = 0x0004003000008D02
	LATEST_VERSION = 0

	GAME_SERVER_ID = 0x3200
	ACCESS_KEY = "ridfebb9"
	NEX_VERSION = 20000

class MiiV1(common.Data):
	def __init__(self, name, unk1, unk2, data):
		self.name = name
		self.unk1 = unk1
		self.unk2 = unk2
		self.data = data

	def get_name(self):
		return "Mii"

	def save(self, stream):
		stream.string(self.name)
		stream.u8(self.unk1)
		stream.u8(self.unk2)
		stream.buffer(self.data.build())

	def load(self, stream):
		self.name = stream.string()
		self.unk1 = stream.u8()
		self.unk2 = stream.u8()
		self.data = miis.MiiData.parse(stream.buffer())
common.DataHolder.register(MiiV1, "MiiV1")
	
class MiiV2(common.Data):
	def __init__(self, name, unk1, unk2, data, datetime):
		self.name = name
		self.unk1 = unk1
		self.unk2 = unk2
		self.data = data
		self.datetime = datetime

	def get_name(self):
		return "MiiV2"
		
	def save(self, stream):
		stream.string(self.name)
		stream.u8(self.unk1)
		stream.u8(self.unk2)
		stream.buffer(self.data.build())
		stream.datetime(self.datetime)
	
	def load(self, stream):
		self.name = stream.string()
		self.unk1 = stream.u8()
		self.unk2 = stream.u8()
		self.data = miis.MiiData.parse(stream.buffer())
		self.datetime = stream.datetime()
common.DataHolder.register(MiiV2, "MiiV2")

	
class PrincipalBasicInfo(common.Data):
	def __init__(self, pid, nnid, mii, unk):
		self.pid = pid
		self.nnid = nnid
		self.mii = mii
		self.unk = unk

	def get_name(self):
		return "PrincipalBasicInfo"

	def save(self, stream):	
		stream.u32(self.pid)
		stream.string(self.nnid)
		stream.add(self.mii)
		stream.u8(self.unk)
		
	def load(self, stream):
		self.pid = stream.u32()
		self.nnid = stream.string()
		self.mii = stream.extract(MiiV2)
		self.unk = stream.u8()
common.DataHolder.register(PrincipalBasicInfo, "PrincipalBasicInfo")
	
	
class NNAInfo(common.Data):
	def __init__(self, principal_info, unk1, unk2):
		self.principal_info = principal_info
		self.unk1 = unk1
		self.unk2 = unk2

	def get_name(self):
		return "NNAInfo"

	def save(self, stream):	
		stream.add(self.principal_info)
		stream.u8(self.unk1)
		stream.u8(self.unk2)
		
	def load(self, stream):
		self.principal_info = stream.extract(PrincipalBasicInfo)
		self.unk1 = stream.u8()
		self.unk2 = stream.u8()
common.DataHolder.register(NNAInfo, "NNAInfo")

		
class GameKey(common.Data):
	def __init__(self, title_id, title_version):
		self.title_id = title_id
		self.title_version = title_version
		
	def get_name(self):
		return "GameKey"
		
	def save(self, stream):
		stream.u64(self.title_id)
		stream.u16(self.title_version)
		
	def load(self, stream):
		self.title_id = stream.u64()
		self.title_version = stream.u16()
common.DataHolder.register(GameKey, "GameKey")

class NintendoPresenceV1(common.Data):
	def __init__(self, unk_u32_1, game_key, message, unk_u32_2, unk_u8, unk_u32_3, unk_u32_4, unk_u32_5, unk_u32_6, unk_buffer):
		self.unk_u32_1 = unk_u32_1
		self.game_key = game_key
		self.message = message
		self.unk_u32_2 = unk_u32_2
		self.unk_u8 = unk_u8
		self.unk_u32_3 = unk_u32_3
		self.unk_u32_4 = unk_u32_4
		self.unk_u32_5 = unk_u32_5
		self.unk_u32_6 = unk_u32_6
		self.unk_buffer = unk_buffer

	def get_name(self):
		return "NintendoPresence"

	def save(self, stream):
		stream.u32(self.unk_u32_1)
		self.game_key.save(stream)
		stream.string(self.message)
		stream.u32(self.unk_u32_2)
		stream.u8(self.unk_u8)
		stream.u32(self.unk_u32_3)
		stream.u32(self.unk_u32_4)
		stream.u32(self.unk_u32_5)
		stream.u32(self.unk_u32_6)
		stream.buffer(self.unk_buffer)

	def load(self, stream):
		self.unk_u32_1 = stream.u32()
		self.game_key = stream.extract(GameKey)
		self.message = stream.string()
		self.unk_u32_2 = stream.u32()
		self.unk_u8 = stream.u8()
		self.unk_u32_3 = stream.u32()
		self.unk_u32_4 = stream.u32()
		self.unk_u32_5 = stream.u32()
		self.unk_u32_6 = stream.u32()
		self.unk_buffer = stream.buffer()
common.DataHolder.register(NintendoPresenceV1, "NintendoPresence")

		
class NintendoPresenceV2(common.Data):
	def __init__(self, flags, is_online, game_key, unk1, message, unk2, unk3,
				 game_server_id, unk4, pid, gathering_id, data, unk5, unk6, unk7):
		self.flags = flags
		self.is_online = is_online
		self.game_key = game_key
		self.unk1 = unk1
		self.message = message
		self.unk2 = unk2
		self.unk3 = unk3
		self.game_server_id = game_server_id
		self.unk4 = unk4
		self.pid = pid
		self.gathering_id = gathering_id
		self.application_data = data
		self.unk5 = unk5
		self.unk6 = unk6
		self.unk7 = unk7
		
	def get_name(self):
		return "NintendoPresenceV2"
		
	def save(self, stream):
		stream.u32(self.flags)
		stream.u8(self.is_online)
		stream.add(self.game_key)
		stream.u8(self.unk1)
		stream.string(self.message)
		stream.u32(self.unk2)
		stream.u8(self.unk3)
		stream.u32(self.game_server_id)
		stream.u32(self.unk4)
		stream.u32(self.pid)
		stream.u32(self.gathering_id)
		stream.buffer(self.application_data)
		stream.u8(self.unk5)
		stream.u8(self.unk6)
		stream.u8(self.unk7)
		
	def load(self, stream):
		self.flags = stream.u32()
		self.is_online = stream.u8()
		self.game_key = stream.extract(GameKey)
		self.unk1 = stream.u8()
		self.message = stream.string()
		self.unk2 = stream.u32()
		self.unk3 = stream.u8()
		self.game_server_id = stream.u32()
		self.unk4 = stream.u32()
		self.pid = stream.u32()
		self.gathering_id = stream.u32()
		self.application_data = stream.buffer()
		self.unk5 = stream.u8()
		self.unk6 = stream.u8()
		self.unk7 = stream.u8()
common.DataHolder.register(NintendoPresenceV2, "NintendoPresenceV2")
		
		
class PrincipalPreference(common.Data):
	def get_name(self):
		return "PrincipalPreference"

	def load(self, stream):
		self.unk1 = stream.bool()
		self.unk2 = stream.bool()
		self.unk3 = stream.bool()
common.DataHolder.register(PrincipalPreference, "PrincipalPreference")
		
		
class Comment(common.Data):
	"""This is the status message shown in the friend list"""
	def get_name(self):
		return "Comment"
	
	def load(self, stream):
		self.unk = stream.u8()
		self.text = stream.string()
		self.changed = stream.datetime()
common.DataHolder.register(Comment, "Comment")
		
		
class FriendInfo(common.Data):
	def get_name(self):
		return "FriendInfo"

	def load(self, stream):
		self.nna_info = stream.extract(NNAInfo)
		self.presence = stream.extract(NintendoPresenceV2)
		self.comment = stream.extract(Comment)
		self.befriended = stream.datetime()
		self.last_online = stream.datetime()
		self.unk = stream.u64()
common.DataHolder.register(FriendInfo, "FriendInfo")
		
		
class FriendRequestMessage(common.Data):
	def get_name(self):
		return "FriendRequestMessage"

	def load(self, stream):
		self.unk1 = stream.u64()
		self.unk2 = stream.u8()
		self.unk3 = stream.u8()
		self.message = stream.string()
		self.unk4 = stream.u8()
		self.string = stream.string()
		self.game_key = stream.extract(GameKey)
		self.datetime = stream.datetime()
		self.expires = stream.datetime()
common.DataHolder.register(FriendRequestMessage, "FriendRequestMessage")
		
		
class FriendRequest(common.Data):
	def get_name(self):
		return "FriendRequest"

	def load(self, stream):
		self.principal_info = stream.extract(PrincipalBasicInfo)
		self.message = stream.extract(FriendRequestMessage)
		self.sent = stream.datetime()
common.DataHolder.register(FriendRequest, "FriendRequest")

		
class BlacklistedPrincipal(common.Data):
	def get_name(self):
		return "BlacklistedPrincipal"

	def load(self, stream):
		self.principal_info = stream.extract(PrincipalBasicInfo)
		self.game_key = stream.extract(GameKey)
		self.since = stream.datetime()
common.DataHolder.register(BlacklistedPrincipal, "BlacklistedPrincipal")
		
		
class PersistentNotification(common.Data):
	def get_name(self):
		return "PersistentNotification"

	def load(self, stream):
		self.unk1 = stream.u64()
		self.unk2 = stream.u32()
		self.unk3 = stream.u32()
		self.unk4 = stream.u32()
		self.string = stream.string()
common.DataHolder.register(PersistentNotification, "PersistentNotification")

class FriendRelationship(common.Data):
	def __init__(self, principal_id, friend_code, is_complete):
		self.principal_id = principal_id
		self.friend_code = friend_code
		self.is_complete = is_complete

	def get_name(self):
		return "FriendRelationship"

	def save(self, stream):
		stream.u32(self.principal_id)
		stream.u64(self.friend_code)
		stream.bool(self.is_complete)

	def load(self, stream):
		self.principal_id = stream.u32()
		self.friend_code = stream.u64()
		self.is_complete = stream.bool()

common.DataHolder.register(FriendRelationship, "FriendRelationship")

class FriendPersistentInfo(common.Data):
	def __init__(self, unk_u32, unk_u8_1, unk_u8_2, unk_u8_3, unk_u8_4, unk_u8_5, game_key, status, unk_timestamp_1, unk_timestamp_2, unk_timestamp_3):
		self.unk_u32 = unk_u32
		self.unk_u8_1 = unk_u8_1
		self.unk_u8_2 = unk_u8_2
		self.unk_u8_3 = unk_u8_3
		self.unk_u8_4 = unk_u8_4
		self.unk_u8_5 = unk_u8_5
		self.game_key = game_key
		self.status = status
		self.unk_timestamp_1 = unk_timestamp_1
		self.unk_timestamp_2 = unk_timestamp_2
		self.unk_timestamp_3 = unk_timestamp_3

	def get_name(self):
		return "FriendPersistentInfo"

	def load(self, stream):
		self.unk_u32 = stream.u32()
		self.unk_u8_1 = stream.u8()
		self.unk_u8_2 = stream.u8()
		self.unk_u8_3 = stream.u8()
		self.unk_u8_4 = stream.u8()
		self.unk_u8_5 = stream.u8()

		self.game_key = stream.extract(GameKey)
		self.status = stream.string()
		self.unk_timestamp_1 = stream.datetime()
		self.unk_timestamp_2 = stream.datetime()
		self.unk_timestamp_3 = stream.datetime()

	def save(self, stream):
		stream.u32(self.unk_u32)
		stream.u8(self.unk_u8_1)
		stream.u8(self.unk_u8_2)
		stream.u8(self.unk_u8_3)
		stream.u8(self.unk_u8_4)
		stream.u8(self.unk_u8_5)
		self.game_key.save(stream)
		stream.string(self.status)
		stream.datetime(self.unk_timestamp_1)
		stream.datetime(self.unk_timestamp_2)
		stream.datetime(self.unk_timestamp_3)

common.DataHolder.register(FriendPersistentInfo, "FriendPersistentInfo")

class FriendPresence(common.Data):
	def __init__(self, pid, nintendo_presence):
		self.pid = pid
		self.nintendo_presence = nintendo_presence

	def get_name(self):
		return "FriendPresence"

	def save(self, stream):
		stream.u32(self.pid)
		self.nintendo_presence.save(stream)

	def load(self, stream):
		self.pid = stream.u32()
		self.nintendo_presence = stream.extract(NintendoPresenceV1)
common.DataHolder.register(FriendPresence, "FriendPresence")

class FriendPicture:
	def __init__(self, unk_u32, data, timestamp):
		self.unk_u32 = unk_u32
		self.data = data
		self.timestamp = timestamp

	def get_name(self):
		return "FriendPicture"

	def save(self, stream):
		raise NotImplementedError("no")

	def load(self, stream):
		self.unk_u32 = data.u32()
		self.data = data.buffer()
		self.timestamp = data.datetime()

common.DataHolder.register(FriendPicture, "FriendPicture")

class MyProfile(common.Data):
	def __init__(self, unk_u8_1, unk_u8_2, unk_u8_3, unk_u8_4, unk_u8_5, unk_u64, unk_string_1, unk_string_2):
		self.unk_u8_1 = unk_u8_1
		self.unk_u8_2 = unk_u8_2
		self.unk_u8_3 = unk_u8_3
		self.unk_u8_4 = unk_u8_4
		self.unk_u8_5 = unk_u8_5
		self.unk_u64 = unk_u64
		self.unk_string_1 = unk_string_1
		self.unk_string_2 = unk_string_2

	def get_name(self):
		return "MyProfile"

	def streamout(self, stream):
		self.unk_u8_1 = stream.u8()
		self.unk_u8_2 = stream.u8()
		self.unk_u8_3 = stream.u8()
		self.unk_u8_4 = stream.u8()
		self.unk_u8_5 = stream.u8()
		self.unk_u64 = stream.u64()
		self.unk_string_1 = stream.string()
		self.unk_string_2 = stream.string()
common.DataHolder.register(MyProfile, "MyProfile")

class FriendsClient:
	METHOD_GET_ALL_INFORMATION = 1
	METHOD_UPDATE_PRESENCE = 13
	
	PROTOCOL_ID = 0x66
	
	def __init__(self, backend):
		self.client = backend.secure_client
	
	def get_all_information(self, nna_info, presence, birthday):
		logger.info("Friends.get_all_information(...)")
		#--- request ---
		stream, call_id = self.client.init_request(self.PROTOCOL_ID, self.METHOD_GET_ALL_INFORMATION)
		stream.add(nna_info)
		stream.add(presence)
		stream.u64(birthday.value)
		self.client.send_message(stream)
		
		#--- response ---
		stream = self.client.get_response(call_id)
		principal_preference = stream.extract(PrincipalPreference)
		comment = stream.extract(Comment)
		friends = stream.list(FriendInfo)
		sent_requests = stream.list(FriendRequest)
		received_requests = stream.list(FriendRequest)
		blacklist = stream.list(BlacklistedPrincipal)
		unk1 = stream.bool()
		notifications = stream.list(PersistentNotification)
		unk2 = stream.u8()
		logger.info("Friends.get_all_information -> ...")
		return principal_preference, comment, friends, sent_requests, received_requests, blacklist, unk1, notifications, unk2
		
	def update_presence(self, presence):
		logger.info("Friends.update_presence(...)")
		#--- request ---
		stream, call_id = self.client.init_request(self.PROTOCOL_ID, self.METHOD_UPDATE_PRESENCE)
		stream.add(presence)
		self.client.send_message(stream)
		
		#--- response ---
		self.client.get_response(call_id)
		logger.info("Friends.update_presence -> done")

class Friends3DSClient:
	METHOD_UPDATE_PROFILE = 0x01
	METHOD_UPDATE_MII =  0x02
	METHOD_UPDATE_MII_LIST = 0x03
	METHOD_UPDATE_PLAYED_GAMES = 0x04
	METHOD_UPDATE_PREFERENCE = 0x05
	METHOD_GET_FRIEND_MII = 0x06
	# 0x07?
	# 0x08?
	# 0x09?
	METHOD_GET_FRIEND_RELATIONSHIPS = 0x0a
	METHOD_ADD_FRIEND_BY_PRINCIPAL_ID = 0x0b
	# 0x0c?
	# 0x0d?
	METHOD_REMOVE_FRIEND = 0x0e
	METHOD_GET_ALL_FRIENDS = 0x0f
	# 0x10?
	METHOD_SYNC_FRIEND = 0x11
	METHOD_UPDATE_PRESENCE = 0x12
	METHOD_UPDATE_FAVORITE_GAME_KEY = 0x13
	METHOD_UPDATE_COMMENT = 0x14
	# 0x15?
	METHOD_GET_FRIEND_PRESENCE = 0x16
	# 0x17?
	METHOD_GET_FRIEND_PICTURE = 0x18
	METHOD_GET_FRIEND_PERSISTENT_INFO = 0x19
	# 0x1a?

	PROTOCOL_ID = 0x65

	def __init__(self, backend):
		self.client = backend.secure_client

	# (1) UpdateProfile
	# takes a MyProfile
	def update_profile(self, profile):
		logger.info("Friends.update_profile()")
		#--- request ---
		stream, call_id = self.client.init_request(self.PROTOCOL_ID, self.METHOD_UPDATE_PROFILE)
		stream.add(profile)
		self.client.send_message(stream)

		#--- response ---
		self.client.get_response(call_id)
		logger.info("Friends.update_profile -> done")

	# (2) UpdateMii
	# takes a MiiV1
	def update_mii(self, mii):
		logger.info("Friends.update_profile()")
		#--- request ---
		stream, call_id = self.client.init_request(self.PROTOCOL_ID, self.METHOD_UPDATE_MII)
		stream.add(mii)
		self.client.send_message(stream)

		#--- response ---
		self.client.get_response(call_id)
		logger.info("Friends.update_profile -> done")

	# (3) UpdateMiiList
	# takes a MiiList
	def update_mii_list(self, mii_list):
		logger.info("Friends.update_mii_list()")
		#--- request ---
		stream, call_id = self.client.init_request(self.PROTOCOL_ID, self.METHOD_UPDATE_MII_LIST)
		stream.add(mii_list)
		self.client.send_message(stream)

		#--- response ---
		self.client.get_response(call_id)
		logger.info("Friends.update_mii_list -> done")

	# (4) UpdatePlayedGames
	# takes a list of PlayedGames
	def update_played_games(self, played_games):
		logger.info("Friends.update_played_games()")
		#--- request ---
		stream, call_id = self.client.init_request(self.PROTOCOL_ID, self.METHOD_UPDATE_PLAYED_GAMES)
		stream.list(played_games, lambda a: stream.add(a))
		self.client.send_message(stream)

		#--- response ---
		self.client.get_response(call_id)
		logger.info("Friends.update_played_games -> done")

	# (5) UpdatePreference
	def update_preference(self, pref_a, pref_b, pref_c):
		logger.info("Friends.update_preference()")
		#--- request ---
		stream, call_id = self.client.init_request(self.PROTOCOL_ID, self.METHOD_UPDATE_PREFERENCE)
		stream.bool(pref_a)
		stream.bool(pref_b)
		stream.bool(pref_c)
		self.client.send_message(stream)

		#--- response ---
		self.client.get_response(call_id)
		logger.info("Friends.update_preference -> done")

	# (10) GetFriendRelationships
	def get_friend_relationships(self, pid_list):
		logger.info("Friends.get_friend_relationships()")
		#--- request ---
		stream, call_id = self.client.init_request(self.PROTOCOL_ID, self.METHOD_GET_FRIEND_RELATIONSHIPS)
		stream.list(pid_list, stream.u32)
		self.client.send_message(stream)

		#--- response ---
		stream = self.client.get_response(call_id)
		relationships = stream.list(lambda: stream.extract(FriendRelationship))
		logger.info("Friends.get_friend_relationships -> done")
		return relationships

	# (11) AddFriendByPrincipalId
	def add_friend_by_principal_id(self, friend_seed, pid):
		logger.info("Friends.add_friend_by_principal_id()")
		#--- request ---
		stream, call_id = self.client.init_request(self.PROTOCOL_ID, self.METHOD_ADD_FRIEND_BY_PRINCIPAL_ID)
		stream.u64(friend_seed)
		stream.u32(pid)
		self.client.send_message(stream)

		#--- response ---
		stream = self.client.get_response(call_id)
		rel = stream.extract(FriendRelationship)
		logger.info("Friends.add_friend_by_principal_id -> done")
		return rel

	# (14) RemoveFriend
	def remove_friend(self, principal_id):
		logger.info("Friends.remove_friend()")
		#--- request ---
		stream, call_id = self.client.init_request(self.PROTOCOL_ID, self.METHOD_REMOVE_FRIEND)
		stream.u32(principal_id)
		self.client.send_message(stream)

		#--- response ---
		stream = self.client.get_response(call_id)
		logger.info("Friends.remove_friend -> done")

	# (15) GetAllFriends
	def get_all_friends(self):
		logger.info("Friends.get_all_friends()")
		#--- request ---
		stream, call_id = self.client.init_request(self.PROTOCOL_ID, self.METHOD_GET_ALL_FRIENDS)
		self.client.send_message(stream)

		#--- response ---
		stream = self.client.get_response(call_id)
		friends = stream.list(lambda: stream.extract(FriendRelationship))
		logger.info("Friends.get_all_friends -> done")
		return friends

	# (17) SyncFriend
	def sync_friend(self, friend_seed, principal_ids, always_empty):
		logger.info("Friends.sync_friend()")
		#--- request ---
		stream, call_id = self.client.init_request(self.PROTOCOL_ID, self.METHOD_SYNC_FRIEND)
		stream.u64(friend_seed)
		stream.list(principal_ids, stream.u32)
		stream.list(always_empty, stream.u32)
		self.client.send_message(stream)

		#--- response ---
		stream = self.client.get_response(call_id)
		friends = stream.list(lambda: stream.extract(FriendRelationship))
		logger.info("Friends.sync_friend -> done")
		return friends

	# (18) UpdatePresence
	# takes a NintendoPresence as well as a boolean to show played game
	def update_presence(self, presence, unk):
		logger.info("Friends.update_presence(...)")
		#--- request ---
		stream, call_id = self.client.init_request(self.PROTOCOL_ID, self.METHOD_UPDATE_PRESENCE)
		stream.add(presence)
		stream.bool(unk)
		self.client.send_message(stream)

		#--- response ---
		self.client.get_response(call_id)
		logger.info("Friends.update_presence -> done")

	# (19) UpdateFavoriteGameKey
	def update_favorite_game_key(self, game_key):
		logger.info("Friends.update_favorite_game_key(...)")
		#--- request ---
		stream, call_id = self.client.init_request(self.PROTOCOL_ID, self.METHOD_UPDATE_FAVORITE_GAME_KEY)
		stream.add(game_key)
		self.client.send_message(stream)

		#--- response ---
		self.client.get_response(call_id)
		logger.info("Friends.update_favorite_game_key -> done")

	# (20) UpdateComment
	def update_comment(self, comment):
		logger.info("Friends.update_comment(...)")
		#--- request ---
		stream, call_id = self.client.init_request(self.PROTOCOL_ID, self.METHOD_UPDATE_COMMENT)
		stream.string(comment)
		self.client.send_message(stream)

		#--- response ---
		self.client.get_response(call_id)
		logger.info("Friends.update_comment -> done")

	# (22) GetFriendPresence
	def get_friend_presence(self, principal_ids):
		logger.info("Friends.get_friend_presence(...)")
		#--- request ---
		stream, call_id = self.client.init_request(self.PROTOCOL_ID, self.METHOD_GET_FRIEND_PRESENCE)
		stream.list(principal_ids, stream.u32)
		self.client.send_message(stream)

		#--- response ---
		stream = self.client.get_response(call_id)
		presences = stream.list(lambda: stream.extract(FriendPresence))
		logger.info("Friends.get_friend_presence -> done")
		return presences

	# (24) GetFriendPicture
	def get_friend_picture(self, principal_ids):
		logger.info("Friends.get_friend_picture(...)")
		#--- request ---
		stream, call_id = self.client.init_request(self.PROTOCOL_ID, self.METHOD_GET_FRIEND_PICTURE)
		stream.list(principal_ids, stream.u32)
		self.client.send_message(stream)

		#--- response ---
		stream = self.client.get_response(call_id)
		pictures = stream.list(lambda: stream.extract(FriendPicture))
		logger.info("Friends.get_friend_picture -> done")
		return pictures

	# (25) GetFriendPersistentInfo
	def get_friend_persistent_info(self, principal_ids):
		logger.info("Friends.get_friend_persistent_info(...)")
		#--- request ---
		stream, call_id = self.client.init_request(self.PROTOCOL_ID, self.METHOD_GET_FRIEND_PERSISTENT_INFO)
		stream.list(principal_ids, stream.u32)
		self.client.send_message(stream)

		#--- response ---
		stream = self.client.get_response(call_id)
		infos = stream.list(lambda: stream.extract(FriendPersistentInfo))
		logger.info("Friends.get_friend_persistent_info -> done")
		return infos
