import { Component, OnInit, ViewChild, Input } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Constants } from '../../app/Constants';

@Component({
  selector: 'app-simulate',
  templateUrl: './simulate.component.html',
  styleUrls: ['./simulate.component.css']
})
export class SimulateComponent implements OnInit {

  @Input('play') play: boolean = false;
  @Input('regionData') regionData: any = {};
  @Input('selectedRegion') selectedRegion: number;
  @Input('viewAll') viewAll: boolean;
  @ViewChild('worldChart') worldChart: any;
  
  public currentTime: number = 0;
  public firstTime: boolean = true;
  public oldRegionData: any = {};
  public worldChartData = {datasets: []};
  public worldOptions = {
    scales: {
      xAxes: [{
          display: false
      }],
      yAxes: [{
        display: false
      }]
    },
    legend: {
      display: false
    },
    tooltips: {
      enabled: false
    },
  };

  public home = {};

  constructor(private httpClient: HttpClient) { }

  ngOnInit(): void {
    this.home = {
      'xmin': this.regionData['xmin'][this.selectedRegion],
      'xmax': this.regionData['xmax'][this.selectedRegion],
      'ymin': this.regionData['ymin'][this.selectedRegion],
      'ymax': this.regionData['ymax'][this.selectedRegion],
    };
  }
  
  getUpdatedWorld(): void {

    if (!this.play) {
      return;
    }
    
    if (!this.isRegionPolicyChanged()) {
      
      this.httpClient.get<any[]>(Constants.getUrl('/get_world')).subscribe(data => {
        this.currentTime = data['time'];
        this.processWorldResponse(data['data']);
      }, error => {
        console.log(error);
      });
      
    } else {

      this.httpClient.post<any>(Constants.getUrl('/get_world'), this.regionData)
      .subscribe(data => {
        this.currentTime = data['time'];
        this.processWorldResponse(data['data']);
        this.oldRegionData = this.cloneRegions();
      }, error => {
        console.log(error);
      });

    }
    
  }

  private processWorldResponse(data): void {
    let colors = data.map(d => this.colorMapper(d));
    if (this.firstTime) {
      let x = this.home['xmin'] - 5;
      let X = this.home['xmax'] + 5;
      let y = this.home['ymin'] - 5;
      let Y = this.home['ymax'] + 5;
      this.worldChartData = {
        datasets: [{
          data: data.map(d => {return {x: d[0], y: d[1]}}),
          pointRadius: ((data.length > 1000) ? 1: 2),
          pointBackgroundColor: colors,
          pointBorderColor: colors
        }, {
          data: [{x: x, y: y}, {x: x, y: Y}],
          type: 'line',
          borderColor: '#ffa500ff',
          borderWidth: 1
        }, {
          data: [{x: x, y: Y}, {x: X, y: Y}],
          type: 'line',
          borderColor: '#ffa500ff',
          borderWidth: 1
        }, {
          data: [{x: X, y: Y}, {x: X, y: y}],
          type: 'line',
          borderColor: '#ffa500ff',
          borderWidth: 1
        }, {
          data: [{x: x, y: y}, {x: X, y: y}],
          type: 'line',
          borderColor: '#ffa500ff',
          borderWidth: 1
        }]
      };
      this.firstTime = false;
    } else {
      this.worldChartData.datasets[0].data = data.map(d => {return {x: d[0], y: d[1]}});
      this.worldChartData.datasets[0].pointBackgroundColor = colors;
      this.worldChartData.datasets[0].pointBorderColor = colors;
      this.worldChart.chart.update();
    }
    this.getUpdatedWorld();
  }

  private isRegionPolicyChanged(): boolean {
    for (let policy in this.regionData) {
      for (let ind in this.regionData[policy]) {
        if (this.regionData[policy][ind] != this.oldRegionData[policy][ind]) {
          return true;
        }
      }
    }
    return false;
  }

  public cloneRegions(): any {
    let obj = {};
    for (let policy in this.regionData) {
      obj[policy] = {};
      for (let ind in this.regionData[policy]) {
        obj[policy][ind] = this.regionData[policy][ind];
      }
    }
    return obj;
  }

  private colorMapper(d): any {

    if (!this.viewAll && (d[0] < this.home['xmin'] || d[0] > this.home['xmax'] || d[1] < this.home['ymin'] || d[1] > this.home['ymax'])) {
      return '#ffffffff'; // outside the country
    }

    if (d[2] == 0)
      return '#a5a5a822'; // removed
    else if (d[3] > 0.0 && d[3] < 0.4)
      return '#ffff00ff'; // infected but not found
    else if (d[3] >= 0.4)
      return '#ff0000ff'; // infected but found
    else
      return '#ffffffff'; // uninfected
  }

}
