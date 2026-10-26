# ═══════════════════════════════════════════════════════════════
# 后端生产镜像（多阶段构建）
#   阶段1 build : 用 Maven 构建 jar
#   阶段2 runtime : 仅 JRE + jar，体积显著更小
# ═══════════════════════════════════════════════════════════════

# ───── 阶段 1：构建 ─────
FROM maven:3.9-eclipse-temurin-21 AS build

WORKDIR /build

# Maven 走镜像源：国内服务器直连 Central 极慢（实测单 POM 4.18s vs 阿里云 0.054s）
COPY maven-settings.xml /root/.m2/settings.xml

# 先只拷 pom 做依赖预热，利用 Docker 层缓存：
# 源码变动时无需重新下载依赖，显著加快重复构建
COPY pom.xml .
RUN mvn -B dependency:go-offline -q || true

COPY src ./src
RUN mvn -B clean package -DskipTests

# ───── 阶段 2：运行 ─────
FROM eclipse-temurin:21-jre-jammy

# 容器内非 root 运行
RUN groupadd -r app && useradd -r -g app app

WORKDIR /app

# 时区与locale，避免日志时间与容器不一致
ENV TZ=Asia/Shanghai \
    LANG=C.UTF-8

# 数据与日志目录（挂载卷时需保持一致）
RUN mkdir -p /data/uploads /data/logs && chown -R app:app /data /app

COPY --from=build --chown=app:app /build/target/*.jar /app/app.jar

USER app

EXPOSE 8080

# 优雅停机：与 application-prod.yml 的 server.shutdown=graceful 配合，
# 收到 SIGTERM 后等待在途请求完成再退出
STOPSIGNAL SIGTERM

# JVM 参数：容器内存感知（G1GC + 限制堆大小 + 打印 GC）
ENV JAVA_OPTS="-XX:MaxRAMPercentage=75 -XX:+UseG1GC -XX:MaxGCPauseMillis=200 -XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/data/logs -Djava.security.egd=file:/dev/./urandom"

HEALTHCHECK --interval=30s --timeout=5s --start-period=120s --retries=5 \
  CMD curl -fsS http://localhost:8080/actuator/health/readiness || exit 1

ENTRYPOINT ["sh", "-c", "exec java $JAVA_OPTS -jar /app/app.jar --spring.profiles.active=prod"]