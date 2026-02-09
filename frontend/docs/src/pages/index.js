import { Redirect } from '@docusaurus/router';
import useBaseUrl from '@docusaurus/useBaseUrl';


export default function Home() {
  const targetUrl = useBaseUrl('I2WG'); // automatically prepends baseUrl
  return <Redirect to={targetUrl} />;
}
