package com.example.mypage

import org.springframework.stereotype.Service

@Service
class MypageService(
    private val mypageRepository: MypageRepository,
    private val legacyClient: LegacyProfileClient,
) {

    data class UpdateProfileRequest(
        val nickname: String,
        val phone: String,
    ) {
        fun toLegacyDataMap(): Map<String, Any> = mapOf(
            "nick" to nickname,
            "tel" to phone,
        )
    }

    fun updateProfile(userId: Long, request: UpdateProfileRequest): MypageResponse {
        val profile = mypageRepository.findByUserId(userId)
            ?: throw IllegalArgumentException("profile not found: $userId")

        profile.nickname = request.nickname
        profile.phone = request.phone
        mypageRepository.save(profile)

        legacyClient.sync(request.toLegacyDataMap())

        return MypageResponse(nickname = profile.nickname, phone = profile.phone)
    }
}

data class MypageResponse(
    val nickname: String,
    val phone: String,
)
