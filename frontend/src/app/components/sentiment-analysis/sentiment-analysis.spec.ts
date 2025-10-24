import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SentimentAnalysis } from './sentiment-analysis';

describe('SentimentAnalysis', () => {
  let component: SentimentAnalysis;
  let fixture: ComponentFixture<SentimentAnalysis>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SentimentAnalysis]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SentimentAnalysis);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
