package com.gametips.platform.module.oauth.repository;

import com.gametips.platform.module.oauth.domain.OAuthAccount;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface OAuthAccountRepository extends JpaRepository<OAuthAccount, Long> {

    Optional<OAuthAccount> findByProviderAndExternalId(String provider, String externalId);
}
