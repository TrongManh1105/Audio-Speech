document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("profile-form");
    const btnSubmit = document.getElementById("btn-submit");
    const spinner = document.getElementById("spinner");
    const btnText = btnSubmit.querySelector(".btn-text");

    const placeholderState = document.getElementById("placeholder-state");
    const resultsContent = document.getElementById("results-content");

    // Inputs & Badges
    const gpaInput = document.getElementById("gpa");
    const gpaBadge = document.getElementById("gpa-badge");
    const ieltsInput = document.getElementById("ielts");
    const ieltsBadge = document.getElementById("ielts-badge");
    const expInput = document.getElementById("work_exp_years");
    const expBadge = document.getElementById("exp-badge");
    const papersInput = document.getElementById("research_papers");
    const papersBadge = document.getElementById("papers-badge");
    const awardsInput = document.getElementById("awards");
    const awardsBadge = document.getElementById("awards-badge");

    // Presets
    const btnPresetStrong = document.getElementById("btn-preset-strong");
    const btnPresetGap = document.getElementById("btn-preset-gap");

    // Tab buttons & panes
    const tabBtns = document.querySelectorAll(".tab-btn");
    const tabPanes = document.querySelectorAll(".tab-pane");
    const btnTabRoadmap = document.getElementById("btn-tab-roadmap");

    // Sync input values to badge labels
    function updateBadges() {
        if (gpaInput && gpaBadge) gpaBadge.textContent = `${parseFloat(gpaInput.value || 0).toFixed(2)} / 4.0`;
        if (ieltsInput && ieltsBadge) ieltsBadge.textContent = `Band ${parseFloat(ieltsInput.value || 0).toFixed(1)}`;
        if (expInput && expBadge) expBadge.textContent = `${parseFloat(expInput.value || 0).toFixed(1)} năm`;
        if (papersInput && papersBadge) papersBadge.textContent = `${papersInput.value || 0} bài`;
        if (awardsInput && awardsBadge) awardsBadge.textContent = `${awardsInput.value || 0} giải`;
    }

    [gpaInput, ieltsInput, expInput, papersInput, awardsInput].forEach(inp => {
        if (inp) inp.addEventListener("input", updateBadges);
    });

    // Preset 1: Hồ sơ Khủng
    btnPresetStrong.addEventListener("click", () => {
        document.getElementById("name").value = "Nguyễn Văn Xuất Sắc";
        document.getElementById("degree_target").value = "Thạc sĩ";
        document.getElementById("major").value = "Khoa học Máy tính / Trí tuệ Nhân tạo";
        document.getElementById("research_interest").value = "Nghiên cứu mô hình ngôn ngữ lớn (LLMs), Học sâu (Deep Learning) và Thị giác máy tính";
        gpaInput.value = "3.92";
        ieltsInput.value = "8.0";
        expInput.value = "2.5";
        papersInput.value = "3";
        awardsInput.value = "4";
        updateBadges();
        form.dispatchEvent(new Event("submit"));
    });

    // Preset 2: Hồ sơ Dưới Chuẩn
    btnPresetGap.addEventListener("click", () => {
        document.getElementById("name").value = "Lê Hoàng Long";
        document.getElementById("degree_target").value = "Thạc sĩ";
        document.getElementById("major").value = "Information Technology / Data Science";
        document.getElementById("research_interest").value = "Data Analysis, Machine Learning cơ bản ứng dụng phân tích kinh doanh";
        gpaInput.value = "2.80";
        ieltsInput.value = "5.5";
        expInput.value = "0.0";
        papersInput.value = "0";
        awardsInput.value = "0";
        updateBadges();
        form.dispatchEvent(new Event("submit"));
    });


    // Tab switching
    tabBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            tabBtns.forEach(b => b.classList.remove("active"));
            tabPanes.forEach(p => p.classList.remove("active"));

            btn.classList.add("active");
            const targetId = btn.getAttribute("data-tab");
            const targetPane = document.getElementById(targetId);
            if (targetPane) targetPane.classList.add("active");
        });
    });

    // Form Submission
    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        // UI Loading State
        btnSubmit.disabled = true;
        btnText.textContent = "Đang tính toán vector & so khớp...";
        spinner.style.display = "block";

        const payload = {
            name: document.getElementById("name").value.trim(),
            degree_target: document.getElementById("degree_target").value,
            major: document.getElementById("major").value.trim(),
            research_interest: document.getElementById("research_interest").value.trim(),
            gpa: parseFloat(gpaInput.value),
            ielts: parseFloat(ieltsInput.value),
            work_exp_years: parseFloat(expInput.value),
            research_papers: parseInt(papersInput.value || 0),
            awards: parseInt(awardsInput.value || 0)
        };

        try {
            const response = await fetch("/api/match", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            const data = await response.json();

            if (data.status === "success") {
                renderResults(data);
            } else {
                alert("Lỗi: " + (data.message || "Không thể xử lý yêu cầu."));
            }
        } catch (err) {
            console.error("Fetch error:", err);
            alert("Lỗi kết nối đến máy chủ. Vui lòng kiểm tra lại terminal!");
        } finally {
            btnSubmit.disabled = false;
            btnText.textContent = "🚀 Phân Tích & So Khớp Học Bổng";
            spinner.style.display = "none";
        }
    });

    function renderResults(data) {
        placeholderState.style.display = "none";
        resultsContent.style.display = "block";

        const candidate = data.candidate;
        document.getElementById("res-candidate-name").textContent = candidate.name;
        document.getElementById("res-profile-strength").innerHTML = `${candidate.profile_strength}<span>/100</span>`;

        const statusPill = document.getElementById("res-overall-status");
        const hasMatched = data.matched_scholarships && data.matched_scholarships.length > 0;
        const hasGaps = data.gap_summary && data.gap_summary.length > 0;

        if (hasMatched && !hasGaps) {
            statusPill.textContent = "ĐỦ ĐIỀU KIỆN ỨNG TUYỂN (HIGH MATCH)";
            statusPill.className = "status-pill status-eligible";
        } else if (hasGaps) {
            statusPill.textContent = "CHƯA ĐỦ ĐIỀU KIỆN SÀN (CÓ GỢI Ý & LỘ TRÌNH)";
            statusPill.className = "status-pill status-ineligible";
        } else {
            statusPill.textContent = "KHẢ THI CÓ ĐIỀU KIỆN";
            statusPill.className = "status-pill status-eligible";
        }

        // Counts
        document.getElementById("count-matched").textContent = data.matched_scholarships ? data.matched_scholarships.length : 0;
        document.getElementById("count-gaps").textContent = data.gap_summary ? data.gap_summary.length : 0;
        document.getElementById("count-safety").textContent = data.safety_alternatives ? data.safety_alternatives.length : 0;

        const userGpa = parseFloat(gpaInput.value || 0).toFixed(2);
        const userIelts = parseFloat(ieltsInput.value || 0).toFixed(1);

        // 1. Render Matched List (Đánh giá học bổng mục tiêu ĐẠT CHUẨN)
        const matchedList = document.getElementById("matched-list");
        matchedList.innerHTML = "";

        if (!data.matched_scholarships || data.matched_scholarships.length === 0) {
            // Trường hợp hồ sơ DƯỚI CHUẨN: KHÔNG gợi ý học bổng đạt chuẩn ở đây
            matchedList.innerHTML = `
                <div class="empty-state-card" style="text-align: center; padding: 40px 20px; background: rgba(239, 68, 68, 0.05); border: 1px dashed rgba(239, 68, 68, 0.3); border-radius: 12px; margin: 10px 0;">
                    <div style="font-size: 48px; margin-bottom: 12px;">🚫</div>
                    <h3 style="color: #f87171; font-size: 18px; margin-bottom: 8px;">Không Có Học Bổng Nào Bạn Đạt Điều Kiện Sàn</h3>
                    <p style="color: #cbd5e1; font-size: 14px; line-height: 1.6; max-width: 520px; margin: 0 auto 14px auto;">
                        Hồ sơ của bạn (GPA <strong>${userGpa}</strong>, IELTS <strong>${userIelts}</strong>) hiện tại <strong>chưa đạt ngưỡng sàn tối thiểu</strong> của bất kỳ chương trình học bổng mục tiêu nào trong danh mục chính.
                    </p>
                    <div style="background: rgba(239, 68, 68, 0.1); border-left: 3px solid #ef4444; border-radius: 6px; padding: 12px 16px; margin: 0 auto 20px auto; max-width: 520px; text-align: left; font-size: 13px; color: #fca5a5;">
                        💡 <strong>Nguyên tắc hệ thống:</strong> Không đưa ra danh sách gợi ý "Đạt chuẩn" khi hồ sơ chưa đủ điều kiện nhằm tránh rủi ro bị từ chối hồ sơ khi nộp thực tế.
                    </div>
                    <div style="display: flex; gap: 12px; justify-content: center; flex-wrap: wrap;">
                        <button type="button" class="btn-jump-tab" style="background: rgba(245, 158, 11, 0.2); border: 1px solid rgba(245, 158, 11, 0.4); color: #fcd34d; padding: 10px 18px; border-radius: 8px; cursor: pointer; font-weight: 600;" onclick="document.getElementById('btn-tab-roadmap').click()">
                            🗺️ Xem Lộ Trình Nâng Chuẩn
                        </button>
                        <button type="button" class="btn-jump-tab" style="background: rgba(59, 130, 246, 0.2); border: 1px solid rgba(59, 130, 246, 0.4); color: #93c5fd; padding: 10px 18px; border-radius: 8px; cursor: pointer; font-weight: 600;" onclick="document.querySelector('[data-tab=tab-safety]').click()">
                            🛡️ Xem Học Bổng Dự Phòng Vừa Sức
                        </button>
                    </div>
                </div>
            `;
        } else {
            // Trường hợp hồ sơ ĐẠT CHUẨN: Hiển thị Top 1 -> Top N
            data.matched_scholarships.forEach((item, idx) => {
                const card = createScholarshipCard(item, idx, "matched", userGpa, userIelts);
                matchedList.appendChild(card);
            });
        }

        // 2. Render Gap Analysis & Roadmap
        const gapContainer = document.getElementById("gap-tags-container");
        gapContainer.innerHTML = "";
        if (data.gap_summary && data.gap_summary.length > 0) {
            data.gap_summary.forEach(gap => {
                const el = document.createElement("div");
                el.className = "gap-item";
                el.innerHTML = `<span>⚠️</span> <div><strong>${gap.field}:</strong> ${gap.text} (Thiếu <strong>${gap.delta}</strong>)</div>`;
                gapContainer.appendChild(el);
            });
        } else {
            gapContainer.innerHTML = `<div style="font-size: 13px; color: #6ee7b7;">✓ Tuyệt vời! Bạn không bị thiếu tiêu chí bắt buộc nào đối với học bổng mục tiêu.</div>`;
        }

        const roadmapTimeline = document.getElementById("roadmap-timeline");
        roadmapTimeline.innerHTML = "";
        if (data.roadmap && data.roadmap.length > 0) {
            data.roadmap.forEach(step => {
                const stepEl = document.createElement("div");
                stepEl.className = "timeline-step";
                stepEl.innerHTML = `
                    <div class="timeline-phase">${step.stage}</div>
                    <div class="timeline-title">${step.title}</div>
                    <div class="timeline-action">${step.action}</div>
                `;
                roadmapTimeline.appendChild(stepEl);
            });
        }

        // Render Ineligible Target Scholarships INSIDE TAB ROADMAP
        const ineligibleSection = document.getElementById("ineligible-section");
        const ineligibleList = document.getElementById("ineligible-list");
        if (ineligibleSection && ineligibleList) {
            ineligibleList.innerHTML = "";
            if (data.ineligible_scholarships && data.ineligible_scholarships.length > 0) {
                ineligibleSection.style.display = "block";
                data.ineligible_scholarships.forEach((item, idx) => {
                    const card = createScholarshipCard(item, idx, "ineligible", userGpa, userIelts);
                    ineligibleList.appendChild(card);
                });
            } else {
                ineligibleSection.style.display = "none";
            }
        }

        // 3. Render Safety Alternatives (Học bổng Dự phòng Vừa Sức <= Hồ sơ)
        const safetyList = document.getElementById("safety-list");
        safetyList.innerHTML = "";

        if (data.safety_alternatives && data.safety_alternatives.length > 0) {
            data.safety_alternatives.forEach((item, idx) => {
                const card = createScholarshipCard(item, idx, "safety", userGpa, userIelts);
                safetyList.appendChild(card);
            });
        } else {
            safetyList.innerHTML = `
                <div class="empty-state-card" style="text-align: center; padding: 40px 20px; background: rgba(59, 130, 246, 0.05); border: 1px dashed rgba(59, 130, 246, 0.3); border-radius: 12px; margin: 10px 0;">
                    <div style="font-size: 48px; margin-bottom: 12px;">🛡️</div>
                    <h3 style="color: #93c5fd; font-size: 17px; margin-bottom: 8px;">Chưa Có Học Bổng Dự Phòng Nào Có Điều Kiện ≤ Hồ Sơ Của Bạn</h3>
                    <p style="color: #cbd5e1; font-size: 13.5px; line-height: 1.6; max-width: 520px; margin: 0 auto 12px auto;">
                        Trong cơ sở dữ liệu học bổng quốc tế hiện tại, hầu hết các chương trình đều có ngưỡng sàn tối thiểu là <strong>GPA ≥ 3.0 / 4.0</strong> và <strong>IELTS ≥ 5.5 - 6.0</strong>.
                    </p>
                    <p style="color: #94a3b8; font-size: 13px; max-width: 520px; margin: 0 auto;">
                        Hệ thống tuân thủ nguyên tắc <strong>không đề xuất học bổng có yêu cầu cao hơn hồ sơ của bạn</strong> làm phương án dự phòng. Bạn hãy xem tab <strong>'🗺️ Lộ Trình & Gap'</strong> để có kế hoạch ôn luyện nâng điểm đạt mốc sàn nhé!
                    </p>
                </div>
            `;
        }

        // Auto switch tab if Ineligible
        if (!hasMatched || hasGaps) {
            btnTabRoadmap.click();
        } else {
            tabBtns[0].click();
        }
    }
});

// ==========================================
// MODAL & CARD CREATION LOGIC
// ==========================================
window.currentScholarshipsMap = {};

function createScholarshipCard(item, idx, type, userGpa, userIelts) {
    window.currentScholarshipsMap[item.id] = item;
    const card = document.createElement("div");

    let badgeHtml = "";
    let rankColorStyle = "";
    let benefitsHtml = "";

    if (type === "matched") {
        const isTop1 = idx === 0;
        card.className = `scholarship-card ${isTop1 ? "card-top-1" : ""}`;
        badgeHtml = isTop1 ? '<div class="card-top-badge">👑 ƯU TIÊN TOP 1</div>' : '<div class="card-top-badge" style="background: #10b981;">✓ ĐẠT CHUẨN</div>';
        benefitsHtml = `<strong>Quyền lợi:</strong> ${item.funding || "Toàn phần / Trợ cấp"}`;
    } else if (type === "ineligible") {
        card.className = "scholarship-card";
        card.style.borderColor = "rgba(239, 68, 68, 0.4)";
        card.style.background = "linear-gradient(135deg, rgba(239, 68, 68, 0.08), rgba(15, 23, 42, 0.7))";
        badgeHtml = '<div class="card-top-badge" style="background: #ef4444; box-shadow: 0 0 12px var(--rose-glow);">❌ BỊ LOẠI VÒNG HỒ SƠ</div>';
        rankColorStyle = 'style="color: #f87171; background: rgba(239, 68, 68, 0.15);"';
        const gapTexts = item.gaps ? item.gaps.map(g => `<span style="color: #fca5a5; font-weight: 600;">! ${g.text}</span>`).join(" &nbsp;|&nbsp; ") : "";
        benefitsHtml = `<div style="background: rgba(239, 68, 68, 0.1); padding: 8px 12px; border-radius: 6px; border-left: 3px solid var(--rose);"><strong>Lý do bị loại:</strong> ${gapTexts}</div>`;
    } else if (type === "safety") {
        card.className = "scholarship-card";
        card.style.borderColor = "rgba(16, 185, 129, 0.35)";
        badgeHtml = '<div class="card-top-badge" style="background: #059669;">🛡️ VỪA SỨC DỰ PHÒNG</div>';
        rankColorStyle = 'style="background: rgba(16, 185, 129, 0.2); color: #34d399;"';
        benefitsHtml = `<strong>Quyền lợi:</strong> ${item.funding}`;
    }

    const sourceTag = item.source_name ? `<span class="meta-tag tag-source">🌐 ${item.source_name}</span>` : "";
    const deadlineTag = item.deadline ? `<span class="meta-tag tag-deadline">⏰ Hạn: ${item.deadline}</span>` : "";

    card.innerHTML = `
        ${badgeHtml}
        <div class="card-title-row">
            <div class="rank-number" ${rankColorStyle}>#${idx + 1}</div>
            <div class="sch-title">${item.title}</div>
        </div>
        <div class="card-meta-tags">
            <span class="meta-tag tag-country">📍 ${item.country || "Quốc tế"}</span>
            <span class="meta-tag tag-degree">🎓 ${item.degree || "Thạc sĩ"}</span>
            ${sourceTag}
            ${deadlineTag}
            <span class="meta-tag tag-vector">⚡ Khớp: ${item.sim_pct}%</span>
        </div>
        <div class="sch-benefits">
            ${benefitsHtml}
        </div>
        <div class="card-footer">
            <span class="criteria-text">Yêu cầu sàn: <strong>GPA ≥ ${item.min_gpa} | IELTS ≥ ${item.min_ielts}</strong></span>
            <div class="card-actions-row">
                <button type="button" class="btn-open-modal" onclick="openScholarshipModal('${item.id}')">
                    🔍 Xem Chi Tiết
                </button>
            </div>
        </div>
    `;
    return card;
}

window.openScholarshipModal = function(id) {
    const item = window.currentScholarshipsMap[id];
    if (!item) return;

    document.getElementById("modal-source").textContent = `🌐 Nguồn cào: ${item.source_name || "Chính thức"}`;
    document.getElementById("modal-title").textContent = item.title;
    document.getElementById("modal-country").textContent = item.country || "Quốc tế";
    document.getElementById("modal-degree").textContent = item.degree || "Thạc sĩ / Cử nhân";
    document.getElementById("modal-deadline").textContent = item.deadline || "Theo thông báo tuyển sinh";
    document.getElementById("modal-major").textContent = item.major || "Mọi ngành";
    document.getElementById("modal-funding").textContent = item.funding || "Toàn phần / Trợ cấp";
    document.getElementById("modal-checklist").textContent = item.checklist || "Bảng điểm, CV tiếng Anh, Thư giới thiệu (LOR), SOP";
    document.getElementById("modal-commitment").textContent = item.commitment || "Theo quy chế học bổng quốc tế";

    const criteriaBox = document.getElementById("modal-criteria");
    criteriaBox.innerHTML = `
        <span class="modal-pill">Điểm GPA tối thiểu: ≥ ${item.min_gpa} / 4.0</span>
        <span class="modal-pill">Ngoại ngữ: IELTS ≥ ${item.min_ielts}</span>
        <span class="modal-pill">Kinh nghiệm: ≥ ${item.min_work_exp} năm</span>
    `;

    const visitBtn = document.getElementById("modal-source-link");
    if (item.link && item.link !== "#") {
        visitBtn.href = item.link;
        visitBtn.style.display = "inline-flex";
        visitBtn.textContent = `🚀 Mở bài viết gốc trên ${item.source_name || "Trang Nguồn"} ↗`;
    } else {
        visitBtn.style.display = "none";
    }

    const modal = document.getElementById("scholarship-modal");
    if (modal) modal.style.display = "flex";
};

window.closeScholarshipModal = function() {
    const modal = document.getElementById("scholarship-modal");
    if (modal) modal.style.display = "none";
};

// Đóng modal khi bấm nút đóng hoặc bấm ra ngoài
document.addEventListener("DOMContentLoaded", () => {
    const btnClose = document.getElementById("btn-close-modal");
    if (btnClose) {
        btnClose.addEventListener("click", window.closeScholarshipModal);
    }
    const modalBackdrop = document.getElementById("scholarship-modal");
    if (modalBackdrop) {
        modalBackdrop.addEventListener("click", (e) => {
            if (e.target === modalBackdrop) {
                window.closeScholarshipModal();
            }
        });
    }
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") {
            window.closeScholarshipModal();
        }
    });
});

