function drawDefectDonutChart() {
    var ctx = document.getElementById('defectDonutChart').getContext('2d');
    var donutChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
        labels: ['불량 부표', '양호 부표'],
        datasets: [{
            data: [50, 50],
            backgroundColor: [
                'rgba(255, 99, 132, 0.7)', // 빨간색
                'rgba(54, 162, 235, 0.7)' // 파란색
            ],
            borderColor: [
                'rgba(255, 99, 132, 1)',
                'rgba(54, 162, 235, 1)'
            ],
            borderWidth: 1
        }]
    },
    options: {
        cutout: '70%' // 도넛의 중앙을 빈 공간으로 남기는 비율
    }
    });
}
drawDefectDonutChart();

function drawDonutChartWithData(buoyData) {
    // 데이터가 배열인지 확인
    if (!Array.isArray(buoyData) || buoyData.length === 0) {
        console.error('Buoy data is empty or not in the correct format');
        return;
    }

    var buoyValue = parseFloat(buoyData[0][1]);
    var defect = 100 - buoyValue;

    // 캔버스 요소 존재 확인
    var canvas = document.getElementById('buoyChart');
    if (!canvas) {
        console.error('Canvas element with id "buoyChart" not found');
        return;
    }

    var ctx = canvas.getContext('2d');
    var donutChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['달성', '미달성'],
            datasets: [{
                data: [buoyValue, defect],
                backgroundColor: [
                    'rgba(255, 99, 132, 0.7)', // 빨간색
                    'rgba(54, 162, 235, 0.7)' // 파란색
                ],
                borderColor: [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            cutout: '70%', // 도넛의 중앙을 빈 공간으로 남기는 비율
            animation: {
                animateRotate: true // 회전 애니메이션 활성화
            },
            tooltips: {
                callbacks: {
                    label: function(tooltipItem, data) {
                        var dataset = data.datasets[tooltipItem.datasetIndex];
                        var total = dataset.data.reduce(function(previousValue, currentValue, currentIndex, array) {
                            return previousValue + currentValue;
                        });
                        var currentValue = dataset.data[tooltipItem.index];
                        var percentage = Math.round((currentValue / total) * 100);
                        return percentage + "%";
                    }
                }
            },
            legend: {
                display: true // 범례 표시 여부
            },
            plugins: {
                afterDraw: function(chart) {
                    console.log('됨!@@@@!~!~!');
                    var width = chart.chart.width,
                        height = chart.chart.height,
                        ctx = chart.chart.ctx;

                    var fontSize = (height / 114).toFixed(2);
                    ctx.font = fontSize + "em sans-serif";
                    ctx.fillStyle = '#fff';
                    var buoyText = buoyData[0][1] + "%";
                    var textX = width / 2;
                    var textY = height / 2;

                    ctx.fillText(buoyText, textX, textY);
                }
            }
        }
    });
}

// 서버에서 부이 데이터 가져오기
fetch('/buoy_data')
    .then(response => response.json())
    .then(data => {
        drawDonutChartWithData(data);
    })
    .catch(error => {
        console.error('Error fetching buoy data:', error);
    });

    function drawFinalDonutChart() {
    var deadline = new Date('2024-08-07'); // 납기일 설정
    var startDay = new Date('2024-04-07'); // 시작일 설정
    var today = new Date();
    var remainingDays = Math.ceil((deadline - today) / (1000 * 60 * 60 * 24)); // 현재 날짜와 납기일 사이의 일 수 계산
    var passedDays = Math.ceil((today - startDay) / (1000 * 60 * 60 * 24)); // 현재 날짜와 시작일 사이의 일 수 계산

    var ctx = document.getElementById('deadlineDonutChart').getContext('2d');
    var donutChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Remaining Days', 'Passed Days'],
            datasets: [{
                data: [remainingDays, passedDays],
                backgroundColor: [
                    'rgba(255, 99, 132, 0.7)', // 빨간색
                    'rgba(54, 162, 235, 0.7)' // 파란색
                ],
                borderColor: [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            title: {
                display: true,
                text: 'Days Remaining and Passed'
            },
            cutout: '70%', // 도넛의 중앙을 빈 공간으로 남기는 비율
            animation: {
                animateRotate: true // 회전 애니메이션 활성화
            },
            tooltips: {
                callbacks: {
                    label: function(tooltipItem, data) {
                        var dataset = data.datasets[tooltipItem.datasetIndex];
                        var total = dataset.data.reduce(function(previousValue, currentValue, currentIndex, array) {
                            return previousValue + currentValue;
                        });
                        var currentValue = dataset.data[tooltipItem.index];
                        var percentage = Math.floor(((currentValue / total) * 100) + 0.5);
                        return percentage + "%";
                    }
                }
            },
            legend: {
                display: true
            }
        }
    });
}
drawFinalDonutChart();

function formatLocalDate(date) {
    const options = { year: 'numeric', month: '2-digit', day: '2-digit' };
    return new Date(date).toLocaleDateString('ko-KR', options);
}

function openChart(chartType) {
    const newWindow = window.open('', '_blank', 'width=1000,height=700');
    const canvasHTML = `
        <canvas id="myChart" width="1000" height="350"></canvas>
        ${chartType === 'growthRate' ? '<canvas id="myChartFullYear" width="1000" height="350"></canvas><canvas id="myChartCurrentYear" width="1000" height="350"></canvas>' : ''}
    `;
    newWindow.document.write(canvasHTML);

    fetch('/weather_data')
        .then(response => response.json())
        .then(data => {
            const dates = data.map(entry => formatLocalDate(entry[0]));
            const growthRates = data.map(entry => entry[7]);
            let labels = dates;
            let datasetLabel, datasetData, borderColor;

            switch (chartType) {
                case 'salinity':
                    datasetLabel = '염분';
                    datasetData = data.map(entry => entry[2]);
                    borderColor = 'rgba(255, 99, 132, 1)';
                    break;
                case 'temperature':
                    datasetLabel = '기온';
                    datasetData = data.map(entry => entry[4]);
                    borderColor = 'rgba(255, 99, 132, 1)';
                    break;
                case 'humidity':
                    datasetLabel = '습도';
                    datasetData = data.map(entry => entry[1]);
                    borderColor = 'rgba(255, 99, 132, 1)';
                    break;
                case 'pressure':
                    datasetLabel = '기압';
                    datasetData = data.map(entry => entry[4]);
                    borderColor = 'rgba(255, 99, 132, 1)';
                    break;
                case 'seaTemperature':
                    datasetLabel = '수온';
                    datasetData = data.map(entry => entry[5]);
                    borderColor = 'rgba(255, 99, 132, 1)';
                    break;
                case 'windSpeed':
                    datasetLabel = '풍속';
                    datasetData = data.map(entry => entry[6]);
                    borderColor = 'rgba(255, 99, 132, 1)';
                    break;
                case 'growthRate':
                    const monthlyData = {};
                    data.forEach(entry => {
                        const date = new Date(entry[0]);
                        const year = date.getFullYear();
                        const month = date.getMonth() + 1;
                        if (!monthlyData[year]) {
                            monthlyData[year] = {};
                        }
                        if (!monthlyData[year][month]) {
                            monthlyData[year][month] = [];
                        }
                        monthlyData[year][month].push(entry);
                    });

                    const currentYear = new Date().getFullYear();
                    const fullYearMonthlyLabels = [];
                    const fullYearMonthlyAverageGrowthRates = [];
                    for (let month = 1; month <= 12; month++) {
                        const growthRates = monthlyData[currentYear][month] ? monthlyData[currentYear][month].map(entry => entry[7]) : [0];
                        const averageGrowthRate = growthRates.reduce((acc, curr) => acc + curr, 0) / growthRates.length;
                        fullYearMonthlyLabels.push(month + '월');
                        fullYearMonthlyAverageGrowthRates.push(averageGrowthRate);
                    }

                    const currentMonth = new Date().getMonth() + 1;
                    const currentYearMonthlyLabels = [];
                    const currentYearMonthlyAverageGrowthRates = [];
                    for (let month = 1; month <= currentMonth; month++) {
                        const growthRates = monthlyData[currentYear][month] ? monthlyData[currentYear][month].map(entry => entry[7]) : [0];
                        const averageGrowthRate = growthRates.reduce((acc, curr) => acc + curr, 0) / growthRates.length;
                        currentYearMonthlyLabels.push(month + '월');
                        currentYearMonthlyAverageGrowthRates.push(averageGrowthRate);
                    }

                    const ctxFullYear = newWindow.document.getElementById('myChartFullYear').getContext('2d');
                    new Chart(ctxFullYear, {
                        type: 'line',
                        data: {
                            labels: fullYearMonthlyLabels,
                            datasets: [{
                                label: '전체 평균 생장률',
                                data: fullYearMonthlyAverageGrowthRates,
                                borderColor: 'rgba(75, 192, 192, 1)',
                                borderWidth: 1,
                                fill: false
                            }]
                        },
                        options: {
                            scales: {
                                y: {
                                    beginAtZero: true
                                }
                            }
                        }
                    });

                    const ctxCurrentYear = newWindow.document.getElementById('myChartCurrentYear').getContext('2d');
                    new Chart(ctxCurrentYear, {
                        type: 'line',
                        data: {
                            labels: currentYearMonthlyLabels,
                            datasets: [{
                                label: '현재 월까지 평균 생장률',
                                data: currentYearMonthlyAverageGrowthRates,
                                borderColor: 'rgba(255, 99, 132, 1)',
                                borderWidth: 1,
                                fill: false
                            }]
                        },
                        options: {
                            scales: {
                                y: {
                                    beginAtZero: true
                                }
                            }
                        }
                    });
                    break;
            }

            const datasets = [{
                label: '생장률',
                data: growthRates,
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1,
                fill: false
            }];

            if (chartType !== 'growthRate') {
                datasets.push({
                    label: datasetLabel,
                    data: datasetData,
                    borderColor: borderColor,
                    borderWidth: 1,
                    fill: false
                });
            }

            const ctx = newWindow.document.getElementById('myChart').getContext('2d');
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: datasets
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        })
        .catch(error => {
            console.error('Error fetching weather data:', error);
        });
}





document.addEventListener("DOMContentLoaded", function() {
    const newsList = document.getElementById('newsList');
    const newsItems = newsList.getElementsByTagName('li');
    let currentIndex = 0;

    function displayNextNewsItem() {
        if (currentIndex > 0) {
            newsItems[currentIndex - 1].style.display = 'none';
        }
        newsItems[currentIndex].style.display = 'list-item';
        currentIndex = (currentIndex + 1) % newsItems.length;
    }

    for (let i = 0; i < newsItems.length; i++) {
        newsItems[i].style.display = 'none';
    }
    displayNextNewsItem();
    setInterval(displayNextNewsItem, 8000);
});

function displayCalendar() {
    var today = new Date();
    var year = today.getFullYear();
    var month = today.getMonth() + 1;
    
    var calendarElement = document.getElementById('calendarItem');
    var calendarHTML = '<table>';
    calendarHTML += '<tr>';
    calendarHTML += '<th colspan="7" class="calendar-month">' + year + '년 ' + month + '월</th>';
    calendarHTML += '</tr>';
    calendarHTML += '<tr>';
    calendarHTML += '<th>일</th>';
    calendarHTML += '<th>월</th>';
    calendarHTML += '<th>화</th>';
    calendarHTML += '<th>수</th>';
    calendarHTML += '<th>목</th>';
    calendarHTML += '<th>금</th>';
    calendarHTML += '<th>토</th>';
    calendarHTML += '</tr>';
    
    var firstDay = new Date(year, month - 1, 1);
    var lastDay = new Date(year, month, 0);
    var firstDayOfWeek = firstDay.getDay();

    calendarHTML += '<tr>';
    for (var i = 0; i < firstDayOfWeek; i++) {
        calendarHTML += '<td></td>';
    }
    for (var i = 1; i <= lastDay.getDate(); i++) {
        var currentDay = new Date(year, month - 1, i);
        var dayOfWeek = currentDay.getDay();
        if (dayOfWeek === 0) {
            calendarHTML += '</tr><tr>';
        }
        calendarHTML += '<td>' + i + '</td>';
    }
    calendarHTML += '</tr>';
    calendarHTML += '</table>';

    calendarElement.innerHTML = calendarHTML;
}

function updateCurrentTime() {
    var now = new Date();
    document.getElementById('currentTime').innerHTML = '<h2>' + now.getFullYear() + '년 ' + (now.getMonth() + 1) + '월 ' + now.getDate() + '일 ' + '<br>' + now.getHours() + '시 ' + now.getMinutes() + '분 ' + now.getSeconds() + '초</h2>';
}

setInterval(updateCurrentTime, 1000);
displayCalendar();

const imageContainer = document.getElementById('imageContainer');
const hoverVideo = imageContainer.querySelector('.hover-video');

imageContainer.addEventListener('mouseenter', () => {
    hoverVideo.style.display = 'block';
    hoverVideo.play();
});

imageContainer.addEventListener('mouseleave', () => {
    hoverVideo.style.display = 'none';
    hoverVideo.pause();
});

