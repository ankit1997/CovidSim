import { Component, ViewChild } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Constants } from '../app/Constants';
import { SimulateComponent } from './simulate/simulate.component';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  
  public play: boolean = false;
  public regionData: any = {};
  public regions: any[] = [];
  public selectedRegion: number = 1;
  public viewAll: boolean = false;

  @ViewChild('simulateComp') simulateComp: SimulateComponent;
  
  constructor(private httpClient: HttpClient) {
  }

  ngOnInit(): void {
    this.getMetaData();
  }

  getRegionsData(): Promise<any> {
    return this.httpClient.get<any>(Constants.getUrl('/get_regions')).toPromise();
  }

  async getMetaData() {
    let data = await this.getRegionsData();
    this.regionData = data;
    this.regions = [];
    for (let i of Object.keys(data['region_id'])) {
      this.regions.push({label: data['region_name'][i], value: data['region_id'][i]});
    }
  }

  onPlayClick() {
    this.play = true;
    this.simulateComp.play = true;
    this.simulateComp.oldRegionData = this.simulateComp.cloneRegions();
    this.simulateComp.getUpdatedWorld();
  }

  onPauseClick() {
    this.play = false;
    this.simulateComp.play = false;
  }

  onResetClick() {
    this.httpClient.get(Constants.getUrl('/reset')).subscribe(_ => {
      this.getMetaData();
      this.onPlayClick();
    });
  }

  onAddPersonClick() {
    this.httpClient.post<any>(Constants.getUrl('/add_person_to_region'), {'region_id': this.selectedRegion, 'num_people': 1})
    .subscribe(data => {}, error => {
      console.log(error);
    });
  }

  onPolicyChange(policy: string, value: number): void {
    this.regionData[policy][this.selectedRegion] = value;
  }

  openInNewTab(url: string) {
    window.open(url, '_blank').focus();
  }

}
