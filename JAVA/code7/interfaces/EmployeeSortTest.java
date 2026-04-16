package interfaces;

import java.util.*;


public class EmployeeSortTest
{
   public static void main(String[] args)
   {
      Employee[] staff = new Employee[3];

      staff[0] = new Employee("Harry Hacker", 35000);
      staff[1] = new Employee("Carl Cracker", 75000);
      staff[2] = new Employee("Tony Tester", 38000);

      Arrays.sort(staff);

      // print out information about all Employee objects
      for (Employee e : staff)
         System.out.println("name=" + e.getName() + ",salary=" + e.getSalary());
      
      Arrays.sort(staff,staff[0]);
      for (Employee e : staff)
          System.out.println("name=" + e.getName() + ",salary=" + e.getSalary());
      
      
      Comparable<Employee>[] staff1=new Employee[3];
      staff1[0] = new Employee("John Smith", 50000);
      staff1[1] = new Employee("Alice Brown", 35000);
      staff1[2] = new Employee("Hell Joo", 38000);
      Arrays.sort(staff1);
      for (Comparable<Employee> c : staff1)
          System.out.println(c.toString());



   }
}