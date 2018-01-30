% include('header.tpl')
<div id="container">
  <div class="offset-xl-2 col-xl-8">
    <h1 class="display-3">{{message}}</h1>
    <table class="table table-striped">
      <thead class="table-dark">
        <tr>
          <th scope="col">Run #</th>
          <th scope="col">Start Time (UTC)</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th scope="row">4</th>
          <td>2018-01-25 22:22</td>
        </tr>
        <tr>
          <th scope="row">3</th>
          <td>2018-01-25 03:29</td>
        </tr>
        <tr>
          <th scope="row">2</th>
          <td>2018-01-25 02:56</td>
        </tr>
        <tr>
          <th scope="row">1</th>
          <td>2018-01-24 23:39</td>
        </tr>
      </tbody>
    </table>
  </div>
</div>
% include('footer.tpl')