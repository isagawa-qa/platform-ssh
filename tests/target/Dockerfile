# L3 SSH target: Rocky Linux 9 running sshd with a known sshd_config.
#
# The public key is passed at build time; no key material is committed.
#   ssh-keygen -t ed25519 -N "" -f <tmp>/l3_key
#   docker build --build-arg AUTHORIZED_KEY="$(cat <tmp>/l3_key.pub)" -t platform-ssh-l3-target tests/target
#   docker run -d --name platform-ssh-l3 -p 2222:22 platform-ssh-l3-target
#
# The validators read /etc/ssh/sshd_config (mode 0600), so the target allows
# root login by key only. That is also why STIG-001 is expected to FAIL here.
FROM rockylinux:9

RUN dnf install -y openssh-server procps-ng && dnf clean all && ssh-keygen -A

COPY sshd_config /etc/ssh/sshd_config
RUN chmod 600 /etc/ssh/sshd_config && mkdir -p /root/.ssh && chmod 700 /root/.ssh

ARG AUTHORIZED_KEY
RUN test -n "$AUTHORIZED_KEY" \
    && printf '%s\n' "$AUTHORIZED_KEY" > /root/.ssh/authorized_keys \
    && chmod 600 /root/.ssh/authorized_keys

RUN /usr/sbin/sshd -t

EXPOSE 22
CMD ["/usr/sbin/sshd", "-D", "-e"]
