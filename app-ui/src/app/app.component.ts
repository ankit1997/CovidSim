import { Component, ViewChild } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Constants } from '../app/Constants';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  
  public play: boolean = false;
  public firstTime: boolean = true;
  public socialDistancing: number = 0.0;
  public regionData: any = {};
  public oldRegionData: any = {};
  public regions: any[] = [];
  public selectedRegion: number;
  
  @ViewChild('worldChart') worldChart: any;
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
    }
  };
  
  constructor(private httpClient: HttpClient) {
  }

  ngOnInit(): void {
    this.firstTime = true;
    this.play = true;
    this.getMetaData();
  }

  getMetaData(): void {
    this.httpClient.get<any>(Constants.getUrl('/get_regions')).subscribe(data => {
      this.regionData = data;
      this.oldRegionData = this.cloneRegions();
      this.regions = [];
      for (let i of Object.keys(data['region_id'])) {
        this.regions.push({label: data['region_name'][i], value: data['region_id'][i]});
      }
      this.getUpdatedWorld();
    });
  }

  onPlayClick() {
    this.play = true;
    this.getUpdatedWorld();
  }

  onPauseClick() {
    this.play = false;
  }

  onResetClick() {
    this.httpClient.get(Constants.getUrl('/reset')).subscribe(_ => {
      this.firstTime = true;
      this.play = true;
      this.getMetaData();
    });
  }

  onPolicyChange(policy: string, value: number): void {
    this.regionData[policy][this.selectedRegion] = value;
  }

  getUpdatedWorld(): void {

    if (!this.play) {
      return;
    }
    
    if (!this.isRegionPolicyChanged()) {
      
      this.httpClient.get<any[]>(Constants.getUrl('/get_world')).subscribe(data => {
        this.processWorldResponse(data);
      }, error => {
        console.log(error);
      });
      
    } else {

      this.httpClient.post<any>(Constants.getUrl('/get_world'), this.regionData)
      .subscribe(data => {
        this.processWorldResponse(data);
        this.oldRegionData = this.cloneRegions();
      }, error => {
        console.log(error);
      });

    }
    
  }

  private processWorldResponse(data): void {
    let colors = data.map(d => this.colorMapper(d));
    if (this.firstTime) {
      this.worldChartData = {
        datasets: [{
          data: data.map(d => {return {x: d[0], y: d[1]}}),
          pointRadius: ((data.length > 1000) ? 1: 2),
          pointBackgroundColor: colors,
          pointBorderColor: colors
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

  private cloneRegions(): any {
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
    if (d[2] == 0)
      return '#a5a5a822'; // removed
    else if (d[3] > 0.0 && d[3] < 0.4)
      return '#ffff00ff'; // infected but not found
    else if (d[3] >= 0.4)
      return '#ff0000ff'; // infected but found
    else
      return '#ffffffff'; // uninfected
  }

  openInNewTab(url: string) {
    window.open(url, '_blank').focus();
  }

}
