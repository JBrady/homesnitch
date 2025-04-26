import { rest } from 'msw';

export const handlers = [
  rest.get('/scan_with_score', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json([
        {
          ip: '192.168.0.1',
          vendor: 'TestCo',
          type: 'Phone',
          query_count: 5,
          data_sent: ['example.com', 'test.org'],
          risk_level: 'low'
        }
      ])
    );
  }),
  rest.get('/agent/test', (req, res, ctx) => {
    return res(ctx.status(200), ctx.json({ status: 'ok', devices: [], results: [] }));
  })
];
