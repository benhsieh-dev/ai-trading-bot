import { TestBed } from '@angular/core/testing';

import { Trading } from './trading';

describe('Trading', () => {
  let service: Trading;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(Trading);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
