document.addEventListener("DOMContentLoaded", function () {
    var cosine_sim = sessionStorage.getItem("cosine_sim");
    var missing_skills = JSON.parse(sessionStorage.getItem("missing_skills"));
    var edu_score = sessionStorage.getItem("edu_score");
    var education_review = JSON.parse(sessionStorage.getItem("education_review"));
    var upgraded_pdf = sessionStorage.getItem("upgraded_pdf");
    console.log("Missing Skills:", missing_skills);

    cosine_sim = Math.round(cosine_sim * 100);
    console.log("Cosine Skills:", cosine_sim);

    var cosine_sim_d = cosine_sim + "%";
    var edu_score_d = edu_score + "%";

    document.getElementById("cosine_sim_display").textContent = cosine_sim_d;
    document.getElementById("edu_score_display").textContent = edu_score_d;

    var progressValue = cosine_sim / 100;
    var progressValue2 = edu_score / 100;

    function getGradient(progressValue) {
        if (progressValue <= 0.20) {
            return ["#ff0000", "#ff0000"];
        } else if (progressValue <= 0.40) {
            return ["#ff0000", "#ff7f00"];
        } else if (progressValue <= 0.60) {
            return ["#ff7f00", "#0000ff"];
        } else if (progressValue <= 0.80) {
            return ["#0000ff", "#00ff00"];
        } else {
            return ["#00ff00", "#008080"];
        }
    }

    function displayUpgradedPDF(pdfPath) {
        var pdfContainer = document.getElementById("upgraded_pdf_display");
        var iframe = document.createElement('iframe');
        iframe.setAttribute("src", pdfPath);
        iframe.setAttribute("width", "100%");
        iframe.setAttribute("height", "600px");
        iframe.setAttribute("frameborder", "0");
        pdfContainer.appendChild(iframe);
    }

    function displayEducationReview(reviewElementId, education_review) {
        var reviewElement = document.getElementById(reviewElementId);
        reviewElement.textContent = education_review;
    }

    function displayMissingSkills(missing_skills) {
        const missingSkillsContainer = document.getElementById("missing_skills_display");
        const skillCounts = missing_skills.reduce((acc, skill) => {
            acc[skill] = (acc[skill] || 0) + 1;
            return acc;
        }, {});
        const words = Object.keys(skillCounts).map(skill => ({text: skill, size: skillCounts[skill] * 15}));
        const layout = d3.layout.cloud()
            .size([1250, 300])
            .words(words)
            .padding(5)
            .rotate(() => Math.floor(Math.random() * 2) * 90)
            .fontSize(d => Math.min(d.size, 60))
            .fontWeight("bold")
            .on("end", draw);
        function draw(words) {
            const svg = d3.select(missingSkillsContainer).append("svg")
                .attr("width", layout.size()[0])
                .attr("height", layout.size()[1])
                .append("g")
                .attr("transform", "translate(" + layout.size()[0] / 2 + "," + layout.size()[1] / 2 + ")")
                .selectAll("text")
                .data(words)
                .enter().append("text")
                .style("font-size", d => d.size + "px")
                .style("font-family", "Arial")
                .style("font-weight", "bold")
                .style("fill", (d, i) => d3.schemeCategory10[i % 10])
                .attr("text-anchor", "middle")
                .attr("transform", d => "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")")
                .text(d => d.text);
        }
        layout.start();
    }

    $(".dashboard-progress-12").circleProgress({
        value: progressValue2,
        size: 125,
        startAngle: -Math.PI,
        thickness: "auto",
        fill: { gradient: getGradient(progressValue2) },
        emptyFill: "rgba(0, 0, 0, .1)",
        animation: { duration: 1200, easing: "circleProgressEasing" },
        animationStartValue: 0,
        reverse: false,
        lineCap: "butt",
        insertMode: "prepend",
    });

    $(".dashboard-progress-11").circleProgress({
        value: progressValue,
        size: 125,
        startAngle: -Math.PI,
        thickness: "auto",
        fill: { gradient: getGradient(progressValue) },
        emptyFill: "rgba(0, 0, 0, .1)",
        animation: { duration: 1200, easing: "circleProgressEasing" },
        animationStartValue: 0,
        reverse: false,
        lineCap: "butt",
        insertMode: "prepend",
    });
});
