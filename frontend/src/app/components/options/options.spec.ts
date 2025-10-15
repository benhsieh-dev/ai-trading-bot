import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Options } from './options';

describe('Options', () => {
  let component: Options;
  let fixture: ComponentFixture<Options>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Options]
    })
    .compileComponents();

    fixture = TestBed.createComponent(Options);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
