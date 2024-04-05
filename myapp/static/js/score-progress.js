// score-progress.js
$(document).ready(function() {
    function addPercentageText(circleSelector, score) {
        var colorGradient;
        // Determine color based on score
        if (score >= 75) {
            colorGradient = ["#76c893", "#4db469"]; // Green gradient for high scores
        } else if (score >= 50) {
            colorGradient = ["#f0db4f", "#ffc300"]; // Yellow gradient for medium scores
        } else {
            colorGradient = ["#ff7e67", "#ff5333"]; // Red gradient for low scores
        }

        $(circleSelector).circleProgress({
            value: score / 100,
            size: 100,
            thickness: 10,
            fill: { gradient: colorGradient }
        }).on('circle-animation-progress', function(event, progress, stepValue) {
            $(this).find('strong').remove(); // Remove previous percentage text if exists
            $(this).append($('<strong style="position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%);">' + (stepValue * 100).toFixed(2) + '%</strong>'));
        });
    }

    // Initialize progress bars for each score
    var scores = {
        '#overallScoreProgress': $('#overallScoreProgress').data('score'),
        '#skillsScoreProgress': $('#skillsScoreProgress').data('score'),
        '#educationScoreProgress': $('#educationScoreProgress').data('score'),
        '#experienceScoreProgress': $('#experienceScoreProgress').data('score')
    };

    Object.keys(scores).forEach(function(selector) {
        var score = scores[selector];
        addPercentageText(selector, score);
    });
});
